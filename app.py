import os
import pandas as pd
import streamlit as st

# ページ幅を最大化
st.set_page_config(layout="wide")

# CSVファイルの読み込み
CSV_FILE = "idol-list.csv"
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE, encoding="shift_jis")
else:
    st.error("CSVファイルが見つかりません！")
    st.stop()

# Streamlitアプリタイトル
st.title("アイドル管理システム")

# フィルタリングセクション
st.subheader("絞り込み条件を選択してください")
col1, col2 = st.columns(2)
with col1:
    selected_skills = st.multiselect(
        "スキルで絞り込む",
        options=df["スキル"].unique(),
        default=[]  # デフォルトは未選択（全表示）
    )
with col2:
    selected_seconds = st.multiselect(
        "秒数で絞り込む",
        options=sorted(df["秒数"].unique()),
        default=[]  # デフォルトは未選択（全表示）
    )

# フィルタリング処理
filtered_df = df.copy()
if selected_skills:
    filtered_df = filtered_df[filtered_df["スキル"].isin(selected_skills)]
if selected_seconds:
    filtered_df = filtered_df[filtered_df["秒数"].isin(selected_seconds)]

# 属性の表示順を設定
attribute_order = {"Cu": 0, "Co": 1, "Pa": 2}
filtered_df["属性順"] = filtered_df["属性"].map(attribute_order)

# デフォルトの特化列名
default_columns = ["ボーカル", "ダンス", "ビジュアル"]
default_colors = {"ボーカル": "#ffe4e1", "ダンス": "#add8e6", "ビジュアル": "#ffffe0"}

# 特化ステータス例外
custom_vertical_axes = {
    "ドミナント・ハーモニー": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"],
    "ミューチャル": ["ボーカル&ダンス", "ダンス&ビジュアル", "ビジュアル&ボーカル"]
}

# 確率の並び順
probability_order = {"低": 0, "中": 1, "高": 2}

# スキルごとにテーブルを表示
for skill in filtered_df["スキル"].unique():
    st.markdown(f"### スキル: {skill}")

    skill_df = filtered_df[filtered_df["スキル"] == skill].copy()

    # 特化ステータス例外の適用
    columns = custom_vertical_axes.get(skill, default_columns)

    # 秒数確率で並べ替え
    skill_df["秒数確率"] = skill_df["秒数"].astype(str) + skill_df["確率"]
    skill_df["確率ソート"] = skill_df["確率"].map(probability_order)
    seconds_probs = sorted(
        skill_df["秒数確率"].dropna().unique(),
        key=lambda x: (int(x[:-1]), probability_order.get(x[-1], 0))
    )

    if not skill_df.empty:
        # 特化ラベルを一度だけ表示
        st.markdown(
            f"<div style='display: flex; justify-content: space-around; padding: 10px; background-color: #f5f5f5; border-radius: 5px;'>"
            + "".join([f"<div style='background-color: {default_colors.get(col, '#ffffff')}; padding: 5px; text-align: center;'>{col}</div>" for col in columns])
            + "</div>",
            unsafe_allow_html=True,
        )

        # 秒数ごとにデータを取得し横並び
        for sec_prob in seconds_probs:
            st.write(f"**秒数: {sec_prob}**")
            cols = st.columns(len(columns))
            for i, col_name in enumerate(columns):
                with cols[i]:
                    # 特化ごとのアイドルを表示
                    idols = skill_df[(skill_df["秒数確率"] == sec_prob) & (skill_df["特化"] == col_name)]
                    if not idols.empty:
                        idols = idols.sort_values(by="属性順")  # 属性順でソート
                        for _, row in idols.iterrows():
                            # 画像を確実に表示
                            image_path = row["画像パス"]
                            if os.path.exists(image_path):
                                st.image(image_path, width=100, use_container_width=False)

                                # アイドル名を独立したテキスト要素で表示（改行をサポート）
                                st.markdown(
                                    f"""
                                    <p style="text-align: left; margin: 0;">
                                        {row["アイドル名"].replace("<br>", "<br />")}
                                    </p>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.error(f"画像が見つかりません: {image_path}")

                            # 詳細情報を表示
                            with st.expander("詳細"):
                                st.write(f"**属性**: {row['属性']}")
                                st.write(f"**特化**: {row['特化']}")
                                st.write(f"**秒数**: {row['秒数']} 秒")
                                st.write(f"**確率**: {row['確率']}")
                                st.write(f"**スキル**: {row['スキル']}")
                                st.write(f"**センター効果**: {row['センター効果']}")
                                st.write(f"**Vo**: {row['Vo']}")
                                st.write(f"**Da**: {row['Da']}")
                                st.write(f"**Vi**: {row['Vi']}")
                                st.write(f"**メモリアルガシャ**: {row['メモリアルガシャ'] if pd.notna(row['メモリアルガシャ']) else 'データなし'}")
                                if skill == "ドミナント・ハーモニー":
                                    st.write(f"**副属性**: {row['副属性']}")
                                    st.write(f"**ドミナント**: {row['ドミナント']}")
