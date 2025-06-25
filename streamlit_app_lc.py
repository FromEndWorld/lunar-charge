import streamlit as st
import pandas as pd
import numpy as np
import itertools

# 设置页面
st.set_page_config(page_title="原神月感电伤害计算器", layout="wide")
st.title("🎮 原神月感电反应伤害精确计算器")
st.caption("表格化参数输入 | 主角色固定为伊涅芙 | 支持1-4名角色 | 最高伤害×1，次高×0.5，第三第四×0.083 | 作者：GPT-4")

# 等级系数表（1-100级）
LEVEL_FACTORS ={
    1: 17.17,
    2: 18.54,
    3: 19.90,
    4: 21.27,
    5: 22.65,
    6: 24.65,
    7: 26.64,
    8: 28.87,
    9: 31.37,
    10: 34.14,
    11: 37.20,
    12: 40.66,
    13: 44.45,
    14: 48.56,
    15: 53.75,
    16: 59.08,
    17: 64.42,
    18: 69.72,
    19: 75.12,
    20: 80.58,
    21: 86.11,
    22: 91.70,
    23: 97.24,
    24: 102.81,
    25: 108.41,
    26: 113.20,
    27: 118.10,
    28: 122.98,
    29: 129.73,
    30: 136.29,
    31: 142.67,
    32: 149.03,
    33: 155.42,
    34: 161.83,
    35: 169.11,
    36: 176.52,
    37: 184.07,
    38: 191.71,
    39: 199.56,
    40: 207.38,
    41: 215.40,
    42: 224.17,
    43: 233.50,
    44: 243.35,
    45: 256.06,
    46: 268.54,
    47: 281.53,
    48: 295.01,
    49: 309.07,
    50: 323.60,
    51: 336.76,
    52: 350.53,
    53: 364.48,
    54: 378.62,
    55: 398.60,
    56: 416.40,
    57: 434.39,
    58: 452.95,
    59: 472.61,
    60: 492.88,
    61: 513.57,
    62: 539.10,
    63: 565.51,
    64: 592.54,
    65: 624.44,
    66: 651.47,
    67: 679.50,
    68: 707.79,
    69: 736.67,
    70: 765.64,
    71: 794.77,
    72: 824.68,
    73: 851.16,
    74: 877.74,
    75: 914.23,
    76: 946.75,
    77: 979.41,
    78: 1011.22,
    79: 1044.79,
    80: 1077.44,
    81: 1110.00,
    82: 1142.98,
    83: 1176.37,
    84: 1210.18,
    85: 1253.84,
    86: 1288.95,
    87: 1325.48,
    88: 1363.46,
    89: 1405.10,
    90: 1446.85,
    91: 1488.22,
    92: 1528.44,
    93: 1580.37,
    94: 1630.85,
    95: 1711.20,
    96: 1780.45,
    97: 1847.32,
    98: 1911.47,
    99: 1972.86,
    100: 2030.07
}

# 初始化角色表格数据
if 'characters_df' not in st.session_state:
    st.session_state.characters_df = pd.DataFrame({
        "启用": [True, False, False, False],
        "角色名": ["伊涅芙", "", "", ""],
        "等级": [90, 90, 90, 90],
        "元素精通": [300, 300, 300, 300],
        "暴击率%": [60.0, 60.0, 60.0, 60.0],
        "暴击伤害%": [150.0, 150.0, 150.0, 150.0],
        "月感电伤害提升%": [0.0, 0.0, 0.0, 0.0]
    })

# 角色数据输入表格
st.header("角色参数设置")
st.info("在下方表格中输入角色参数（支持复制粘贴批量编辑）")

# 使用可编辑表格 - 修复角色名输入问题
edited_df = st.data_editor(
    st.session_state.characters_df,
    column_config={
        "启用": st.column_config.CheckboxColumn(
            "启用",
            help="是否启用该角色",
            default=False,
        ),
        "角色名": st.column_config.TextColumn(
            "角色名",
            help="角色名称",
            required=True,
        ),
        "等级": st.column_config.NumberColumn(
            "等级",
            help="角色等级 (1-90)",
            min_value=1,
            max_value=90,
            step=1,
            format="%d",
        ),
        "元素精通": st.column_config.NumberColumn(
            "元素精通",
            help="元素精通值 (0-3000)",
            min_value=0,
            max_value=3000,
            step=50,
            format="%d",
        ),
        "暴击率%": st.column_config.NumberColumn(
            "暴击率%",
            help="暴击率百分比 (0-100)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            format="%.1f",
        ),
        "暴击伤害%": st.column_config.NumberColumn(
            "暴击伤害%",
            help="暴击伤害百分比 (0-300)",
            min_value=0.0,
            max_value=300.0,
            step=1.0,
            format="%.1f",
        ),
        "月感电伤害提升%": st.column_config.NumberColumn(
            "月感电伤害提升%",
            help="月感电伤害提升百分比 (0-200)",
            min_value=0.0,
            max_value=200.0,
            step=1.0,
            format="%.1f",
        ),
    },
    # 移除角色名列的禁用 - 允许输入其他角色名
    hide_index=True,
    num_rows="fixed",
    use_container_width=True
)

# 保存编辑后的数据
st.session_state.characters_df = edited_df.copy()

# 确保主角色伊涅芙存在且固定
if edited_df.iloc[0]["角色名"] != "伊涅芙":
    st.warning("主角色名已重置为'伊涅芙'")
    edited_df.at[0, "角色名"] = "伊涅芙"
    st.session_state.characters_df = edited_df.copy()

# 确保主角色启用
if not edited_df.iloc[0]["启用"]:
    st.warning("主角色必须启用，已自动启用")
    edited_df.at[0, "启用"] = True
    st.session_state.characters_df = edited_df.copy()

# 提取有效的角色数据
characters = []
for i, row in edited_df.iterrows():
    if row["启用"] and row["角色名"]:  # 只处理启用且有角色名的行
        characters.append({
            "name": row["角色名"],
            "level": int(row["等级"]),
            "em": int(row["元素精通"]),
            "crit_rate": row["暴击率%"] / 100,
            "crit_dmg": row["暴击伤害%"] / 100,
            "aggrevate_bonus": row["月感电伤害提升%"] / 100
        })

# 确保主角色伊涅芙存在
if not any(char["name"] == "伊涅芙" for char in characters):
    st.error("必须包含主角色'伊涅芙'！请确保第一行角色名为'伊涅芙'且已启用。")
    st.stop()

# 伤害计算公式
def calculate_base_damage(level, em, aggrevate_bonus):
    """计算基础伤害（不含暴击）"""
    # 获取等级系数
    level_factor = LEVEL_FACTORS.get(level, 0.74)  # 默认使用90级系数
    
    # 计算精通加成 (符合新公式)
    em_bonus = (em * 5) / (em + 2100)
    
    # 计算基础伤害 (符合新公式)
    base_damage = level_factor * 3 * 0.6 * 1.14 * (1 + em_bonus + aggrevate_bonus)
    return base_damage

# 全局参数设置 - 放在角色参数下方
st.divider()
st.header("全局参数设置")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    monster_resistance = st.number_input(
        "怪物抗性%", 
        min_value=-100, 
        max_value=1000, 
        value=10, 
        step=1,
        help="怪物基础抗性百分比（-100%到1000%）"
    )

with col2:
    resistance_reduction = st.number_input(
        "减抗值%", 
        min_value=0, 
        max_value=200, 
        value=0, 
        step=1,
        help="减抗效果百分比（0%到200%）"
    )

# 计算抗性区 - 根据新规则更新
def calculate_resistance_factor(resist, reduction):
    """计算抗性区系数（根据新规则）"""
    # 计算有效抗性（百分比）
    effective_resist = resist - reduction
    
    # 根据有效抗性范围应用不同公式
    if effective_resist >= 75:  # 抗性≥75%
        return 1 / (1 + 4 * effective_resist / 100)
    elif effective_resist >= 0:  # 0%≤抗性＜75%
        return 1 - effective_resist / 100
    else:  # 抗性＜0%
        return 1 - effective_resist / 200  # 负抗性收益减半

resistance_factor = calculate_resistance_factor(monster_resistance, resistance_reduction)

# 计算按钮
if st.button("精确计算伤害期望", type="primary"):
    if not characters:
        st.error("请启用至少一个角色！")
        st.stop()
        
    n = len(characters)  # 实际角色数量
    st.success(f"已输入 {n} 名角色参数，开始计算...")
    
    # 根据角色数量设置权重
    if n == 1:
        weights = [1.0]
    elif n == 2:
        weights = [1.0, 0.5]
    elif n == 3:
        weights = [1.0, 0.5, 1/12]
    else:  # n == 4
        weights = [1.0, 0.5, 1/12, 1/12]
    
    # 计算每个角色的基础伤害
    char_data = []
    for char in characters:
        base_dmg = calculate_base_damage(char["level"], char["em"], char["aggrevate_bonus"])
        crit_dmg = base_dmg * (1 + char["crit_dmg"])
        char_data.append({
            "name": char["name"],
            "base_damage": base_dmg,
            "crit_damage": crit_dmg,
            "crit_rate": char["crit_rate"],
            "non_crit_rate": 1 - char["crit_rate"]
        })
    
    # 生成所有暴击组合 (2^n种)
    crit_combinations = list(itertools.product([0, 1], repeat=n))
    
    # 计算每种组合的概率和加权伤害
    scenario_results = []
    total_expectation = 0
    
    for combo in crit_combinations:
        # 计算该组合的概率
        prob = 1.0
        for i, crit_state in enumerate(combo):
            if crit_state == 1:  # 暴击
                prob *= char_data[i]["crit_rate"]
            else:  # 未暴击
                prob *= char_data[i]["non_crit_rate"]
        
        # 跳过概率为0的组合
        if prob == 0:
            continue
        
        # 计算该组合下每个角色的实际伤害
        damages = []
        for i, crit_state in enumerate(combo):
            damage = char_data[i]["crit_damage"] if crit_state == 1 else char_data[i]["base_damage"]
            damages.append({
                "name": char_data[i]["name"],
                "damage": damage,
                "crit": "暴击" if crit_state == 1 else "未暴击"
            })
        
        # 按伤害值排序
        sorted_damages = sorted(damages, key=lambda x: x["damage"], reverse=True)
        
        # 应用权重计算加权伤害
        weighted_damage = 0
        for i, dmg in enumerate(sorted_damages):
            weight = weights[i] if i < len(weights) else weights[-1]
            dmg["weight"] = weight
            dmg["weighted"] = dmg["damage"] * weight
            weighted_damage += dmg["weighted"]
        
        # 计算该组合的期望贡献
        expectation = weighted_damage * prob
        
        # 存储结果
        scenario_results.append({
            "组合": "|".join([f"{d['name']}({'暴' if c==1 else '未'})" for d, c in zip(damages, combo)]),
            "概率": prob,
            "加权伤害": weighted_damage,
            "期望贡献": expectation,
            "详情": sorted_damages.copy()
        })
        
        # 累加总期望
        total_expectation += expectation
    
    # 应用抗性区
    total_expectation *= resistance_factor
    
    # 计算有效抗性用于显示
    effective_resist = monster_resistance - resistance_reduction
    
    # 显示最终结果
    st.header("伤害计算结果")
    
    # 创建两列布局
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("总伤害期望", f"{int(total_expectation):,}")
        st.metric("计算组合数", len(scenario_results))
        st.metric("参与角色数", n)
        
        # 显示抗性区信息（更新公式说明）
        st.info("**抗性区计算**:")
        st.write(f"- 怪物抗性: {monster_resistance}%")
        st.write(f"- 减抗值: {resistance_reduction}%")
        st.write(f"- 有效抗性: {effective_resist}%")
        st.write(f"- 抗性系数: {resistance_factor:.4f}")
        
        # 显示权重说明
        st.info("**伤害权重规则**:")
        st.write(f"- 🥇 最高伤害角色 ×{weights[0]}")
        if n >= 2:
            st.write(f"- 🥈 次高伤害角色 ×{weights[1]}")
        if n >= 3:
            st.write(f"- 🥉 第三角色 ×{weights[2]}")
        if n >= 4:
            st.write(f"- 第四角色 ×{weights[3]}")
    
    with col2:
        # 显示角色基础伤害
        st.subheader("角色基础伤害")
        base_df = pd.DataFrame([
            {
                "角色": char["name"],
                "等级": char["level"],
                "等级系数": LEVEL_FACTORS[char["level"]],
                "元素精通": char["em"],
                "月感电加成": f"{char['aggrevate_bonus']*100:.1f}%",
                "基础伤害": int(char_data[i]["base_damage"]),
                "暴击伤害": int(char_data[i]["crit_damage"]),
                "暴击率": f"{char['crit_rate']*100:.1f}%"
            }
            for i, char in enumerate(characters)
        ])
        st.dataframe(base_df, hide_index=True)
        
        # 显示所有组合的概率分布
        st.subheader("暴击组合概率分布 (前10)")
        prob_df = pd.DataFrame({
            "暴击组合": [r["组合"] for r in scenario_results],
            "概率": [f"{r['概率']*100:.4f}%" for r in scenario_results],
            "加权伤害": [int(r["加权伤害"]) for r in scenario_results]
        })
        # 只显示前10个组合
        st.dataframe(prob_df.sort_values("概率", ascending=False).head(10), hide_index=True)
    
    # 详细计算说明（更新抗性区公式）
    with st.expander("计算原理说明"):
        st.markdown(f"""
        **精确计算流程**:
        1. 计算所有可能的暴击组合 ({2**n}种情况)
        2. 对每种组合：
           - 计算发生概率 = Π(各角色暴击状态对应概率)
           - 计算每个角色的实际伤害（暴击状态用暴击伤害，否则用基础伤害）
           - 按伤害值从高到低排序
           - 应用权重系数：{', '.join([f'第{i+1}高×{w}' for i, w in enumerate(weights)])}
           - 计算该组合的加权总伤害
           - 期望贡献 = 加权总伤害 × 发生概率
        3. 所有组合的期望贡献之和即为总期望伤害
        4. 应用抗性区系数：总期望伤害 × {resistance_factor:.4f}
        
        **基础伤害公式**:
        ```
        基础伤害 = 等级系数 × 3 × 0.6 × 1.14 × (1 + (元素精通 × 5)/(元素精通 + 2100) + 月感电伤害提升)
        暴击伤害 = 基础伤害 × (1 + 暴击伤害%)
        ```
        
        **抗性区公式（更新）**:
        ```
        有效抗性 = 怪物抗性% - 减抗值%
        
        如果有效抗性 ≥ 75%:
            抗性系数 = 1 / (1 + 4 × 有效抗性)
        如果 0% ≤ 有效抗性 < 75%:
            抗性系数 = 1 - 有效抗性
        如果有效抗性 < 0%:
            抗性系数 = 1 - (有效抗性 / 2)
        ```
        
        **等级系数表**:
        """)
        
        # 显示等级系数表
        levels = list(LEVEL_FACTORS.keys())
        factors = list(LEVEL_FACTORS.values())
        level_df = pd.DataFrame({
            "等级": levels,
            "系数": factors
        })
        st.dataframe(level_df.set_index("等级"), height=300)

# 批量操作指南
with st.expander("📋 批量操作指南"):
    st.markdown("""
    **如何批量输入数据:**
    1. **复制数据**：从Excel或其他表格软件复制数据
    2. **全选表格**：点击表格左上角的空白区域全选表格
    3. **粘贴数据**：按 `Ctrl+V` (Windows) 或 `Cmd+V` (Mac) 粘贴
    4. **格式要求**：确保列顺序为：启用,角色名,等级,元素精通,暴击率%,暴击伤害%,月感电伤害提升%
    
    **注意事项:**
    - 第一行角色名固定为"伊涅芙"，粘贴时会自动重置
    - 第一行启用状态固定为True，粘贴时会自动重置
    - 其他行角色名可自由编辑
    - 粘贴后请检查数据格式是否正确
    """)

# 页脚
st.divider()
st.caption("原神月感电伤害计算器 v10.1 | 优化参数输入布局 | 支持更大范围的抗性计算 | 数据仅供参考，实际游戏效果以官方为准")