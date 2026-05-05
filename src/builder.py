import datetime
from typing import List, Dict, Any
from src.query import RAGQuery

class SkillBuilder:
    """
    Automates generating a comprehensive 'skill.md' reference text
    by querying the RAG system across predefined domain concepts.
    """
    
    # Global extraction questions mapped to skill.md sections
    # Key: Section Name, Value: (Question, Context Injection Flag)
    GLOBAL_QUESTIONS = {
        "Overview": "這個知識庫的核心內容、範疇與邊界為何？請用一段話總結 (200字以內)。",
        "Core Concepts": "這個知識庫涉及哪些最重要的核心概念？請列出 5-15 個概念並附帶簡短說明。",
        "Key Trends": "在目前提供的資料中，有哪些重要的研究方向、政策發展或趨勢？請列出 3-10 個方向。",
        "Key Entities": "涉及哪些重要的作者、機構、工具、框架、專利或資料集？請分類條列。",
        "Methodology & Best Practices": "這個領域中主要使用的方法論、計畫流程、作業程序或最佳實踐有哪些？",
        "Knowledge Gaps & Limitations": "目前的知識庫有哪些明顯的侷限性？例如未涵蓋的子主題、資料截止日期、或可能存在衝突的細節。"
    }
    
    # Representative Example Q&A
    EXAMPLE_QUESTIONS = [
        "哪些事業需要繳交碳費？",
        "什麼是自主減量計畫？",
        "歐盟 CBAM 規範主要針對哪些對象？"
    ]
    
    def __init__(self, query_engine: RAGQuery):
        """
        Initializes the SkillBuilder with a connected RAGQuery engine.
        """
        self.query_engine = query_engine
        
    def build_skill_content(self, n_results: int = 3, use_mock: bool = False) -> str:
        """
        Synthesizes foundational knowledge and constructs a structured skill.md.
        """
        vector_store = self.query_engine.vector_store
        
        # 1. Metadata Generation
        today = datetime.date.today().strftime("%Y-%m-%d")
        source_count = vector_store.get_source_count()
        sources = vector_store.get_unique_sources()
        
        lines = []
        lines.append("# Skill: Taiwan Carbon Market & Regulatory Insights\n")
        
        lines.append("## Metadata")
        lines.append("- **知識領域**：臺灣碳費政策、減量指引及歐盟 CBAM 規範")
        lines.append(f"- **資料來源數量**：{source_count} 份文件")
        lines.append(f"- **最後更新時間**：{today}")
        lines.append("- **適用 Agent 類型**：法規研究助手 / 碳資產顧問 / 政策分析機器人\n")
        
        # 2. Global Section Extraction
        for section, question in self.GLOBAL_QUESTIONS.items():
            lines.append(f"## {section}")
            
            result = self.query_engine.query(
                question=question, 
                n_results=n_results * 2, # Use more context for global summaries
                use_mock=use_mock
            )
            
            lines.append(f"{result['answer']}\n")
            
        # 3. Example Q&A
        lines.append("## Example Q&A")
        for q in self.EXAMPLE_QUESTIONS:
            result = self.query_engine.query(
                question=q, 
                n_results=n_results, 
                use_mock=use_mock
            )
            lines.append(f"### Q: {q}")
            lines.append(f"**A:** {result['answer']}\n")
            
        # 4. Source References
        lines.append("## Source References")
        for s in sources:
            lines.append(f"- {s}")
            
        return "\n".join(lines)
    
    def build_conversation_summary(self, context: str, n_results: int = 3, use_mock: bool = False) -> str:
        """
        Synthesizes the provided conversation history into a structured summary.
        """
        if not context or not context.strip():
            raise ValueError("傳入的對話紀錄 (context) 為空，無法生成總結。")

        today = datetime.date.today().strftime("%Y-%m-%d")
        
        summary_prompt = f"""你現在是一個專業的知識總結助理。
        請根據以下提供的「歷史對話紀錄」，整理出一份結構化的 Markdown 總結報告。

        報告請包含以下區塊：
        ## 1. 核心探討議題
        (簡述使用者主要詢問了哪些問題或領域)

        ## 2. 關鍵解答與資料依據
        (條列對話中提供的具體解答，並務必保留或標示原對話中出現的資料來源、出處或 [引用標籤])

        ## 3. 資訊缺口或限制
        (指出對話中 AI 表示無法完整回答、資料不足、或是尚待釐清的部分。若無，請簡短說明「無明顯資訊缺口」)

        請不要虛構對話中未提及的資訊。

        【歷史對話紀錄】：
        {context}
        """
        
        result = self.query_engine.query(
            question=summary_prompt, 
            n_results=n_results, 
            use_mock=use_mock
        )
        
        lines = []
        lines.append("# 對話重點與依據總結 (Conversation Summary)\n")
        lines.append(f"- **生成日期**：{today}")
        lines.append(f"- **來源**：歷史對話紀錄萃取\n")
        lines.append("---\n")
        lines.append(result.get("answer", "無法生成總結內容。"))
            
        return "\n".join(lines)
