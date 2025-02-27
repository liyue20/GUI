# test_runner.py
import os
import json
from src.services.style_agent.rule_generator import StyleRuleGenerator
from src.services.style_agent.runtime import RuntimeManager

def test_single_theme():
    """测试单个主题"""
    try:
        # 1. 加载布局数据
        with open("test/test_data/layout.json", "r", encoding="utf-8") as f:
            layout_info = json.load(f)
        
        # 2. 设置基本参数
        card_size = {
            "width": 1000,
            "height": 800
        }
        theme_color = "#4CAF50"  # 蓝色主题
        
        # 3. 创建输出目录
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 4. 生成样式规则
        generator = StyleRuleGenerator(
            layout_info=layout_info,
            card_size=card_size,
            theme_color=theme_color
        )
        style_rules = generator.generate()
        
        # 5. 使用运行时管理器生成HTML
        runtime = RuntimeManager(
            layout_info=layout_info,
            card_size=card_size,
            style_rules=style_rules
        )
        
        # 6. 保存结果
        html_path = os.path.join(output_dir, "index.html")
        css_path = os.path.join(output_dir, "styles.css")
        rules_path = os.path.join(output_dir, "rules.json")
        
        # 保存HTML
        runtime.save_html(html_path)
        print(f"HTML已保存至: {html_path}")
        
        # 保存样式
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(generator.generate_css())
        print(f"CSS已保存至: {css_path}")
        
        # 保存规则
        with open(rules_path, "w", encoding="utf-8") as f:
            json.dump(style_rules, f, indent=2, ensure_ascii=False)
        print(f"规则已保存至: {rules_path}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    test_single_theme()