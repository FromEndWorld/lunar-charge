import streamlit as st
import pandas as pd
import numpy as np
import itertools

# 设置页面
st.set_page_config(page_title="原神月感电伤害计算器", layout="wide")
st.title("🎮 原神月感电反应伤害精确计算器")
st.caption("主角色固定为伊涅芙 | 支持1-4名角色 | 最高伤害×1，次高×0.5，第三第四×0.083 | 作者：GPT-4")

# 角色数据输入表单
st.header("角色参数设置")
cols = st.columns(4)
characters = []

# 动态角色输入 - 第一个角色固定为伊涅芙
for i in range(4):
    with cols[i]:
        # 第一个角色固定为伊涅芙，始终启用
        if i == 0:
            # 显示固定角色
            st.subheader(f"主角色")
            st.markdown("**伊涅芙**")
            
            # 固定名称，不可修改
            name = "伊涅芙"
            
            # 显示可修改的参数
            level = st.number_input(f"等级", min_value=1, max_value=90, value=90, key=f"level_0")
            em = st.number_input(f"元素精通", min_value=0, max_value=1500, value=300, key=f"em_0")
            crit_rate = st.slider(f"暴击率%", min_value=0.0, max_value=100.0, value=60.0, key=f"cr_0") / 100
            crit_dmg = st.slider(f"暴击伤害%", min_value=0.0, max_value=300.0, value=150.0, key=f"cd_0") / 100
            
            # 保存角色数据
            characters.append({
                "name": name,
                "level": level,
                "em": em,
                "crit_rate": crit_rate,
                "crit_dmg": crit_dmg
            })
        
        # 其他角色可启用/禁用
        else:
            # 添加角色启用开关
            enabled = st.checkbox(f"启用角色 {i+1}", value=False, key=f"enable_{i}")
            
            if enabled:
                st.subheader(f"角色 {i+1}")
                name = st.text_input(f"角色名", key=f"name_{i}", placeholder="必填", value="")
                
                if name:  # 只有填写了角色名才显示其他输入
                    level = st.number_input(f"等级", min_value=1, max_value=90, value=90, key=f"level_{i}")
                    em = st.number_input(f"元素精通", min_value=0, max_value=1500, value=300, key=f"em_{i}")
                    crit_rate = st.slider(f"暴击率%", min_value=0.0, max_value=100.0, value=60.0, key=f"cr_{i}") / 100
                    crit_dmg = st.slider(f"暴击伤害%", min_value=0.0, max_value=300.0, value=150.0, key=f"cd_{i}") / 100
                    
                    # 保存角色数据
                    characters.append({
                        "name": name,
                        "level": level,
                        "em": em,
                        "crit_rate": crit_rate,
                        "crit_dmg": crit_dmg
                    })
                else:
                    st.warning("请输入角色名")
            else:
                # 禁用状态下的占位符
                st.subheader(f"角色 {i+1} (未启用)")
                st.caption("勾选上方开关启用此角色")

# 伤害计算公式
def calculate_base_damage(level, em):
    """计算基础伤害（不含暴击）"""
    base_damage = 120 * (1 + level/90)  # 基础伤害随等级成长
    reaction_bonus = 2.78 * em / (em + 1400)  # 元素精通加成公式
    return base_damage * (1 + reaction_bonus)

# 计算按钮
if st.button("精确计算伤害期望", type="primary"):
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
        base_dmg = calculate_base_damage(char["level"], char["em"])
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
    
    # 显示最终结果
    st.header("伤害计算结果")
    
    # 创建两列布局
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("总伤害期望", f"{int(total_expectation):,}")
        st.metric("计算组合数", len(scenario_results))
        st.metric("参与角色数", n)
        
        # 显示权重说明
        st.info("**伤害权重规则**:")
        st.write(f"- 🥇 最高伤害角色 ×{weights[0]}")
        if n >= 2:
            st.write(f"- 🥈 次高伤害角色 ×{weights[1]}")
        if n >= 3:
            st.write(f"- 🥉 第三角色 ×{weights[2]}")
        if n >= 4:
            st.write(f"- 第四角色 ×{weights[3]}")
        
        # 显示角色基础伤害
        st.subheader("角色基础伤害")
        base_df = pd.DataFrame([
            {
                "角色": char["name"],
                "基础伤害": int(char["base_damage"]),
                "暴击伤害": int(char["crit_damage"]),
                "暴击率": f"{char['crit_rate']*100:.1f}%"
            } for char in char_data
        ])
        st.dataframe(base_df, hide_index=True)
    
    with col2:
        # 显示所有组合的概率分布
        st.subheader("暴击组合概率分布")
        prob_df = pd.DataFrame({
            "暴击组合": [r["组合"] for r in scenario_results],
            "概率": [f"{r['概率']*100:.4f}%" for r in scenario_results],
            "加权伤害": [int(r["加权伤害"]) for r in scenario_results]
        })
        st.dataframe(prob_df.sort_values("概率", ascending=False), hide_index=True)
        
        # 显示最高概率组合详情
        if scenario_results:
            max_prob_scenario = max(scenario_results, key=lambda x: x["概率"])
            with st.expander(f"最高概率组合: {max_prob_scenario['组合']} (概率: {max_prob_scenario['概率']*100:.2f}%)"):
                det_df = pd.DataFrame(max_prob_scenario["详情"])
                det_df["伤害"] = det_df["damage"].astype(int)
                det_df["权重"] = det_df["weight"]
                det_df["加权伤害"] = det_df["weighted"].astype(int)
                st.dataframe(det_df[["name", "伤害", "crit", "权重", "加权伤害"]].rename(
                    columns={"name": "角色", "crit": "暴击情况"}), hide_index=True)
    
    # 详细计算说明
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
        3. 所有组合的期望贡献之和即为最终期望伤害
        
        **基础伤害公式**:
        ```
        基础伤害 = 120 × (1 + 等级/90)
        精通加成 = 2.78 × 元素精通 ÷ (元素精通 + 1400)
        基础伤害 = 基础伤害 × (1 + 精通加成)
        暴击伤害 = 基础伤害 × (1 + 暴击伤害%)
        ```
        
        **数学表达式**:
        ```
        总期望 = Σ[P(暴击组合) × Σ(角色伤害 × 对应权重)]
        ```
        *注：公式参数可根据游戏实际机制调整*
        """)
else:
    # 检查其他启用的角色是否填写完整
    incomplete = False
    for i in range(1, 4):
        if st.session_state.get(f"enable_{i}", False):
            if f"name_{i}" not in st.session_state or not st.session_state[f"name_{i}"]:
                incomplete = True
                break
    
    if incomplete:
        st.error("请确保所有启用的角色都已填写名称！")
    else:
        st.info("点击按钮计算伤害期望")

# 页脚
st.divider()
st.caption("原神月感电伤害计算器 v7.0 | 主角色固定为伊涅芙 | 数据仅供参考，实际游戏效果以官方为准")