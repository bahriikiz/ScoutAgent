import streamlit as st
from agent import parse_instruction
from db import (
    init_db, add_task, get_active_tasks, save_snapshot, get_last_snapshot,
    count_tasks, count_snapshots, count_changes, last_change_time,
    delete_task
)
from scheduler import run_task

st.set_page_config(page_title="Scout Agent", page_icon="🕵️", layout="centered")

# --- Initialize DB (only first run) ---
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state["db_initialized"] = True

st.title("🕵️ Scout Agent Dashboard")
st.markdown("Akıllı Web İzleyici | Scout Agent PoC")

# --- Mini Dashboard / İstatistik Kutuları ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Görev Sayısı", count_tasks())
col2.metric("Toplam Kontrol", count_snapshots())
col3.metric("Değişiklik Yakalandı", count_changes())
son_deg = last_change_time()
col4.metric("Son Değişiklik", son_deg if son_deg else "—")

# --- Bildirimler (in-memory) ---
if "notifs" not in st.session_state:
    st.session_state.notifs = []

# --- Görev Frekansını Okunabilir Göster (saat+dakika) ---
def freq_human_readable(freq: float) -> str:
    h = int(freq)
    m = int(round((freq - h) * 60))
    if h and m:
        return f"{h} saat {m} dakika"
    elif h:
        return f"{h} saat"
    elif m:
        return f"{m} dakika"
    else:
        return f"{freq:.2f} saat"

# --- Yeni Görev Ekleme ve Onaylama ---
with st.expander("➕ Yeni İzleme Görevi Ekle", expanded=True):
    instruction = st.text_input(
        "Doğal dilde görev girin",
        value="https://example.com/jobs every 1 hour 30 minutes check for new listings",
        key="instruction_input"
    )
    if st.button("Görevi Çözümle", key="parse_btn"):
        try:
            details = parse_instruction(instruction)
            st.session_state["pending_task"] = details
            st.success(
                f"Görev çözümlendi: {details['url']} | {freq_human_readable(details['frequency'])} | {details['task_prompt']}"
            )
        except Exception as e:
            st.error(f"Hata: {e}")

    if "pending_task" in st.session_state:
        details = st.session_state["pending_task"]
        with st.form("confirm_task_form"):
            st.markdown(f"""
            **URL:** {details['url']}  
            **Frekans:** {freq_human_readable(details['frequency'])}  
            **Açıklama:** {details['task_prompt']}
            """)
            confirm = st.form_submit_button("Onayla ve Kaydet")
            if confirm:
                try:
                    task_id = add_task(
                        recruiter_id="recruiter_1",
                        url=details["url"],
                        frequency=details["frequency"],
                        task_prompt=details["task_prompt"]
                    )
                    st.session_state.notifs.append(f"Görev {task_id} eklendi: {details['url']}")
                    st.success("Görev başarıyla eklendi.")
                    del st.session_state["pending_task"]
                except Exception as e:
                    st.error(f"Kaydedilirken hata: {e}")

# --- Bildirimler Paneli ---
if st.session_state.notifs:
    st.info("🔔 " + " | ".join(st.session_state.notifs[-3:]))

# --- Görev Listesi (Aktif Olanlar) ---
st.subheader("📝 Aktif Görevler")
tasks = get_active_tasks()
if not tasks:
    st.warning("Aktif görev yok.")
else:
    for t in tasks:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(f"**{t['url']}**\n\n_{t['task_prompt']}_")
            col2.markdown(f"⏰ {freq_human_readable(t['frequency'])}")
            col3.button(
                f"Şimdi Kontrol Et",
                key=f"run_{t['task_id']}",
                on_click=lambda t=t: st.session_state.update({"run_task_id": t['task_id']})
            )
            # Sil Butonu
            sil = col4.button("🗑️", key=f"del_{t['task_id']}")
            # Durum gösterimi
            col3.markdown(f"Durum: `{t['status']}`")

            # Anlık kontrol ve değişiklik tespiti
            if st.session_state.get("run_task_id") == t["task_id"]:
                with st.spinner("Sayfa kontrol ediliyor..."):
                    prev = get_last_snapshot(t["task_id"])
                    run_task(t)
                    curr = get_last_snapshot(t["task_id"])
                    if prev and curr and prev["content_hash"] != curr["content_hash"]:
                        st.success("⚡️ Değişiklik tespit edildi!")
                        from scraper import compute_diff
                        diff = compute_diff(prev["raw_html"], curr["raw_html"])
                        with st.expander("Değişiklik Detayı"):
                            st.code(diff)
                    elif not prev:
                        st.info("İlk snapshot kaydedildi.")
                    else:
                        st.info("Değişiklik yok.")
                del st.session_state["run_task_id"]

            if sil:
                delete_task(t['task_id'])
                st.success(f"Görev silindi: {t['task_id']}")
                st.rerun()

# --- Hakkında/Yardım ---
with st.expander("ℹ️ Hakkında / Yardım"):
    st.markdown("""
    Bu arayüz, Scout Agent PoC'nin Streamlit tabanlı panelidir.
    - Doğal dil ile görev ekleyin (ör: `https://example.com/jobs every 1 hour 30 minutes check for new jobs`)
    - Görevi onaylayıp kaydedin.
    - Görevleri manuel veya arka planda kontrol edin.
    - Değişiklik bildirimlerini alın.
    """)
