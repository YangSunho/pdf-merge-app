import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
import io

# 상단 제목
st.title("📄 PDF 병합기")

# (특정 페이지 다음에 선택 페이지 삽입)을 다음 줄에, 글자 크기 작게(예: h4)
st.markdown("### (특정 페이지 다음에 선택 페이지 삽입)")

# 제작자 표시 (작게, 보통 텍스트)
st.write("제작자: 양선호")

uploaded_files = st.file_uploader("PDF 파일을 업로드하세요", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_pages = []
    page_images = []
    file_bytes = []

    for file_idx, uploaded_file in enumerate(uploaded_files):
        file_bytes.append(uploaded_file.read())
        images = convert_from_bytes(file_bytes[-1], size=(120, 170))
        for page_idx, image in enumerate(images):
            label = f"{uploaded_file.name} - p{page_idx + 1}"
            all_pages.append((file_idx, page_idx, label))
            page_images.append((label, image))

    current_order = st.session_state.get("current_order", [label for label, _ in page_images])

    st.markdown("### 현재 페이지 순서")
    cols = st.columns(min(len(current_order), 5))
    for idx, label in enumerate(current_order):
        for lbl, img in page_images:
            if lbl == label:
                cols[idx % 5].image(img, caption=label, width=100)

    st.markdown("---")
    st.markdown("### 이동할 페이지를 선택하세요")
    # 체크박스로 이동할 페이지 선택
    move_pages = []
    for label in current_order:
        checked = st.checkbox(label, value=False, key="chk_" + label)
        if checked:
            move_pages.append(label)

    st.markdown("### 선택한 페이지를 어디 다음에 넣을까요?")
    # 기준 페이지 선택용 selectbox (이동할 페이지들은 제외)
    candidates = [p for p in current_order if p not in move_pages]
    if candidates:
        target_page = st.selectbox("기준 페이지 선택", options=candidates)
    else:
        st.info("이동할 페이지 외에 기준으로 삼을 페이지가 없습니다.")
        target_page = None

    if st.button("선택한 페이지 이동"):
        if not move_pages:
            st.warning("이동할 페이지를 선택하세요.")
        elif not target_page:
            st.warning("기준 페이지를 선택하세요.")
        else:
            # 현재 순서 리스트에서 이동할 페이지들 제거
            new_order = [p for p in current_order if p not in move_pages]
            # 기준 페이지 인덱스 찾기
            idx = new_order.index(target_page)
            # 기준 페이지 다음 위치에 선택 페이지 삽입
            new_order = new_order[:idx+1] + move_pages + new_order[idx+1:]
            current_order = new_order
            st.session_state["current_order"] = current_order
            st.success("페이지 이동 완료!")

    st.markdown("---")
    st.markdown("### 이동 후 페이지 순서 미리보기")
    cols = st.columns(min(len(current_order), 5))
    for idx, label in enumerate(current_order):
        for lbl, img in page_images:
            if lbl == label:
                cols[idx % 5].image(img, caption=label, width=100)

    if st.button("병합된 PDF 다운로드"):
        writer = PdfWriter()
        for label in current_order:
            for (file_idx, page_idx, lbl) in all_pages:
                if lbl == label:
                    reader = PdfReader(io.BytesIO(file_bytes[file_idx]))
                    writer.add_page(reader.pages[page_idx])
                    break
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        st.download_button(
            label="병합된 PDF 다운로드",
            data=output,
            file_name="merged_output.pdf",
            mime="application/pdf"
        )
