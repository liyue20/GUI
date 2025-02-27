from ..rule_generator import StyleRuleGenerator

def main():
    # 创建样式生成器实例
    layout_info = {
        'density': 'comfortable',      # 可选值: 'compact', 'comfortable', 'spacious'
        'text_density': 'comfortable'  # 可选值: 'compact', 'comfortable', 'spacious'
    }
    
    card_size = {
        'width': 1200,
        'height': 800
    }
    
    try:
        # 使用预设创建生成器
        generator = StyleRuleGenerator.from_preset(
            layout_info=layout_info,
            card_size=card_size,
            preset_name="elegant_spacious"
        )

        # 生成样式规则
        style_rules = generator.generate()
        print("Style rules generated successfully!")

        # 生成CSS
        css = generator.generate_css()
        print("\nGenerated CSS:")
        print(css[:500] + "...\n")  # 只打印前500个字符

        # 保存CSS到文件
        with open('generated_style.css', 'w', encoding='utf-8') as f:
            f.write(css)
        print("CSS has been saved to 'generated_style.css'")

    except Exception as e:
        print(f"Error generating styles: {str(e)}")

if __name__ == "__main__":
    main() 