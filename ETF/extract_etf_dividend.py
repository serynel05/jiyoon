import re
from pathlib import Path
import pandas as pd
from typing import Tuple

from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.worksheet import Worksheet


def parse_kakao_pension_txt(text: str) -> pd.DataFrame:
    lines = [ln.strip() for ln in text.splitlines()]

    records = []
    current_etf = None

    etf_pat = re.compile(r"^■\s*ETF명\s*:\s*(.+?)\s*$")
    amt_pat = re.compile(r"^■\s*입금액\s*:\s*([0-9,]+)\s*원?\s*$")

    for ln in lines:
        m_etf = etf_pat.match(ln)
        if m_etf:
            current_etf = m_etf.group(1).strip()
            continue

        m_amt = amt_pat.match(ln)
        if m_amt and current_etf:
            amt = int(m_amt.group(1).replace(",", ""))
            records.append({"ETF명": current_etf, "입금액(원)": amt})
            current_etf = None

    return pd.DataFrame(records)


def build_report(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        summary = pd.DataFrame(columns=["ETF명", "총 입금액(원)", "건수"])
        return df, summary

    summary = (
        df.groupby("ETF명", as_index=False)
          .agg(**{"총 입금액(원)": ("입금액(원)", "sum"),
                 "건수": ("입금액(원)", "count")})
          .sort_values(["총 입금액(원)", "ETF명"], ascending=[False, True])
          .reset_index(drop=True)
    )
    return df, summary


def format_number_columns(ws: Worksheet, col_indices, start_row: int, end_row: int, fmt: str = "#,##0"):
    """지정한 열 인덱스(1-based)의 숫자 표시 형식을 엑셀에 적용"""
    for col_idx in col_indices:
        col_letter = get_column_letter(col_idx)
        for r in range(start_row, end_row + 1):
            ws[f"{col_letter}{r}"].number_format = fmt


def append_total_row(ws: Worksheet, label_col: int, sum_col: int, start_data_row: int, end_data_row: int):
    """
    하단에 총합 행 추가:
      - label_col: "총합" 텍스트가 들어갈 열
      - sum_col: 합계 수식이 들어갈 열
    """
    total_row = end_data_row + 1

    # 라벨
    ws.cell(row=total_row, column=label_col, value="총합")
    ws.cell(row=total_row, column=label_col).font = Font(bold=True)
    ws.cell(row=total_row, column=label_col).alignment = Alignment(horizontal="right")

    # 합계 수식
    sum_col_letter = get_column_letter(sum_col)
    ws.cell(row=total_row, column=sum_col, value=f"=SUM({sum_col_letter}{start_data_row}:{sum_col_letter}{end_data_row})")
    ws.cell(row=total_row, column=sum_col).font = Font(bold=True)
    ws.cell(row=total_row, column=sum_col).number_format = "#,##0"

    # (선택) 총합 행 전체 굵게 처리하고 싶으면 아래처럼 확장 가능
    # for c in range(1, ws.max_column + 1):
    #     ws.cell(row=total_row, column=c).font = Font(bold=True)


def main(input_txt_path: str, output_xlsx_path: str):
    text = Path(input_txt_path).read_text(encoding="utf-8")
    df = parse_kakao_pension_txt(text)
    detail, summary = build_report(df)

    with pd.ExcelWriter(output_xlsx_path, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="요약(ETF별)")
        detail.to_excel(writer, index=False, sheet_name="상세(추출원문)")

        # openpyxl 워크북/시트 핸들
        wb = writer.book
        ws_sum = wb["요약(ETF별)"]
        ws_det = wb["상세(추출원문)"]

        # ===== 요약 시트: 콤마 포맷 + 총합 =====
        # pandas가 쓴 데이터는 1행이 헤더, 2행부터 데이터
        summary_data_start = 2
        summary_data_end = ws_sum.max_row  # 현재는 마지막 데이터 행

        if summary_data_end >= summary_data_start:
            # "총 입금액(원)" 열(2번째 열)에 콤마 포맷
            format_number_columns(
                ws_sum,
                col_indices=[2],
                start_row=summary_data_start,
                end_row=summary_data_end,
                fmt="#,##0"
            )

            # 하단 총합 행 추가: 라벨은 1열, 합계는 2열
            append_total_row(
                ws_sum,
                label_col=1,
                sum_col=2,
                start_data_row=summary_data_start,
                end_data_row=summary_data_end
            )

        # ===== 상세 시트도 입금액 콤마 표시 원하면 적용 =====
        detail_data_start = 2
        detail_data_end = ws_det.max_row
        if detail_data_end >= detail_data_start:
            # 상세 시트의 "입금액(원)"은 2번째 열
            format_number_columns(
                ws_det,
                col_indices=[2],
                start_row=detail_data_start,
                end_row=detail_data_end,
                fmt="#,##0"
            )

    print(f"완료: {output_xlsx_path}")
    print(f"- 추출 {len(detail)}건, ETF {len(summary)}종")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("사용법: python extract_etf_dividend.py <input.txt> <output.xlsx>")
        raise SystemExit(1)
    main(sys.argv[1], sys.argv[2])
