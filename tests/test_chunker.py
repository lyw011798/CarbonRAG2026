import pytest
from src.chunker import ChunkStrategy


# ──────────────────────────────────────────────
# Strategy 1: Taiwan Legal Articles (第X條)
# ──────────────────────────────────────────────

class TestLegalArticleStrategy:
    """Tests for splitting on Taiwan legal article boundaries (第X條)."""
    
    def test_splits_on_article_boundaries(self):
        """Articles should be split at 第X條 markers with correct metadata."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "This is the preamble.\n"
            "第一條\n"
            "This is the first article text. It defines the purpose of the act.\n"
            "\n"
            "第二條之三\n"
            "This is an amended article with a sub-number. Very important context here.\n"
            "\n"
            "第三條\n"
            "This is the third article ensuring the strategy triggers properly.\n"
        )
        metadata = {"source": "test_act.txt"}
        
        # Act
        chunks = chunker.split_text(text, metadata)
        
        # Assert
        assert len(chunks) == 4
        assert chunks[0]['metadata']['article'] == 'Preamble'
        assert chunks[0]['text'] == 'This is the preamble.'
        assert chunks[1]['metadata']['article'] == '第一條'
        assert chunks[1]['text'].startswith('第一條')
        assert "purpose of the act" in chunks[1]['text']
        assert chunks[1]['metadata']['source'] == "test_act.txt"
        assert chunks[2]['metadata']['article'] == '第二條之三'
        assert chunks[2]['text'].startswith('第二條之三')

    def test_sub_chunks_long_articles(self):
        """Articles longer than max_chunk_size should be sub-chunked."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=100)
        text = "第一條\n" + ("A" * 50 + "\n") * 5 + "\n第二條\nText2\n第三條\nText3"
    
        # Act
        chunks = chunker.split_text(text)
    
        # Assert
        assert len(chunks) > 1
        # At least one chunk should have '第一條'
        article_names = [c['metadata']['article'] for c in chunks]
        assert '第一條' in article_names
        for chunk in chunks:
            assert len(chunk['text']) <= 160  # some tolerance for header injection

    def test_no_preamble_when_starts_with_article(self):
        """No preamble chunk if text starts directly with an article."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = "第一條\nContent 1.\n第二條\nContent 2.\n第三條\nContent 3."
    
        # Act
        chunks = chunker.split_text(text)
    
        # Assert
        assert chunks[0]['metadata']['article'] == '第一條'
        assert all(c['metadata']['article'] != 'Preamble' for c in chunks)


# ──────────────────────────────────────────────
# Strategy 2: EU Regulation Articles (Article X)
# ──────────────────────────────────────────────

class TestEURegulationStrategy:
    """Tests for splitting on EU regulation article boundaries."""
    
    def test_splits_on_article_boundaries(self):
        """EU articles should be split at 'Article N' markers."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "REGULATION (EU) 2023/956\n"
            "Whereas:\n"
            "(1) Some preamble recital text.\n"
            "Article 1\n"
            "Subject matter\n"
            "This Regulation establishes a CBAM.\n"
            "Article 2\n"
            "Scope\n"
            "1. This Regulation applies to goods listed in Annex I.\n"
        )
        metadata = {"source": "CBAM.txt"}
        
        # Act
        chunks = chunker.split_text(text, metadata)
        
        # Assert
        assert len(chunks) == 3  # preamble + Article 1 + Article 2
        assert chunks[0]['metadata']['article'] == 'Preamble'
        assert 'Whereas' in chunks[0]['text']
        assert chunks[1]['metadata']['article'] == 'Article 1'
        assert 'Subject matter' in chunks[1]['text']
        assert chunks[2]['metadata']['article'] == 'Article 2'
        assert 'Scope' in chunks[2]['text']
        assert chunks[2]['metadata']['source'] == "CBAM.txt"

    def test_handles_chapter_context(self):
        """Chapter headers should be preserved in chunk text without splitting there."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "CHAPTER I\n"
            "SUBJECT MATTER\n"
            "Article 1\n"
            "Subject matter content.\n"
            "CHAPTER II\n"
            "OBLIGATIONS\n"
            "Article 4\n"
            "Importation of goods.\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert — Chapters should NOT create separate chunks, only Articles do
        article_names = [c['metadata']['article'] for c in chunks]
        assert 'Article 1' in article_names
        assert 'Article 4' in article_names

    def test_ignores_article_word_in_body_text(self):
        """'Article' in body text (not at line start as header) should not cause splits."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "Article 1\n"
            "This regulation refers to Article 191 of the Treaty.\n"
            "Article 2\n"
            "Scope of the regulation.\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert — only 2 chunks, not 3
        assert len(chunks) == 2
        assert "Article 191" in chunks[0]['text']


# ──────────────────────────────────────────────
# Strategy 3: Government Form Tables (表/附表)
# ──────────────────────────────────────────────

class TestFormTableStrategy:
    """Tests for splitting on government form table headers (表 X / 附表 X-Y)."""
    
    def test_splits_on_table_headers(self):
        """Text should be split at 表 X and 附表 X-Y boundaries."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "自主減量計畫書\n"
            "申請資料\n"
            "表 C\n"
            "項次 填表說明\n"
            "1 事業名稱：公司名稱填寫。\n"
            "附表 C－A\n"
            "計畫邊界設定及說明\n"
            "1.計畫邊界說明：請說明本自主減量計畫之邊界設定。\n"
            "表 G\n"
            "指定目標計算背景資料\n"
        )
        metadata = {"source": "form.txt"}
        
        # Act
        chunks = chunker.split_text(text, metadata)
        
        # Assert
        assert len(chunks) >= 3  # preamble + 表 C + 附表 C-A + (表 G may be short)
        
        table_articles = [c['metadata']['article'] for c in chunks]
        assert any('表 C' in a for a in table_articles)
        assert any('附表 C－A' in a or '附表 C-A' in a for a in table_articles)

    def test_preserves_form_content(self):
        """Form content should be retained intact within table chunks."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "表 R\n"
            "序號 減量措施 製程及設備名稱\n"
            "A 轉換低碳燃料 鍋爐\n"
            "B 提升能源效率 空壓機\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert
        assert len(chunks) == 1
        assert '轉換低碳燃料' in chunks[0]['text']
        assert '提升能源效率' in chunks[0]['text']
        assert chunks[0]['metadata']['article'] == '表 R'


# ──────────────────────────────────────────────
# Strategy 4: Numbered Sections (X.Y + 一、二、三、)
# ──────────────────────────────────────────────

class TestNumberedSectionStrategy:
    """Tests for splitting on numbered/outlined section headers."""
    
    def test_splits_on_arabic_section_headers(self):
        """Text should be split at X.Y section boundaries."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "第一章 簡介\n"
            "1.1 國家溫室氣體排放清冊背景資訊\n"
            "台灣因應氣候變遷編製國家清冊。\n"
            "1.2 清冊準備之組織制度安排\n"
            "由環境部統籌辦理清冊相關工作。\n"
            "1.3 清冊準備流程\n"
            "清冊準備流程包含資料蒐集、排放計算等步驟。\n"
        )
        metadata = {"source": "report.txt"}
        
        # Act
        chunks = chunker.split_text(text, metadata)
        
        # Assert
        assert len(chunks) >= 3  # preamble may be included + 3 sections
        
        section_articles = [c['metadata']['article'] for c in chunks]
        assert any('1.1' in a for a in section_articles)
        assert any('1.2' in a for a in section_articles)
        assert any('1.3' in a for a in section_articles)

    def test_section_content_preserved(self):
        """Section content should be fully preserved in the chunk."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "1.1 排放概述\n"
            "台灣2023年排放量為280百萬公噸。\n"
            "1.2 趨勢分析\n"
            "排放量呈下降趨勢。\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert
        assert len(chunks) == 2
        assert '280百萬公噸' in chunks[0]['text']
        assert '下降趨勢' in chunks[1]['text']

    def test_splits_on_chinese_numeral_outlines(self):
        """Text should be split at Chinese numeral outline boundaries (一、二、)."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "碳費徵收費率\n"
            "公告事項：\n"
            "一、碳費徵收費率分為一般費率及優惠費率，如附表。\n"
            "二、一般費率為中央主管機關依本法第二十八條規定訂定，供碳費徵收對象據以計算繳交碳費之費率。\n"
            "三、優惠費率為中央主管機關依本法第二十九條規定訂定。\n"
        )
        metadata = {"source": "fee_rate.txt"}
        
        # Act
        chunks = chunker.split_text(text, metadata)
        
        # Assert
        section_articles = [c['metadata']['article'] for c in chunks]
        assert any('一' in a for a in section_articles)
        assert any('二' in a for a in section_articles)
        assert any('三' in a for a in section_articles)

    def test_chinese_numeral_content_preserved(self):
        """Chinese numeral outline content should be preserved in chunks."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "一、法源依據。（第一條）\n"
            "二、依本辦法得提出自主減量計畫申請之事業。（第二條）\n"
            "三、申請自主減量計畫應檢具之文件及計畫內容。（第三條）\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert
        assert len(chunks) == 3
        assert '法源依據' in chunks[0]['text']
        assert '第二條' in chunks[1]['text']
        assert '第三條' in chunks[2]['text']

    def test_legal_takes_priority_over_chinese_outline(self):
        """第X條 should take priority even when Chinese numeral outlines exist."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "一、法源依據\n"
            "二、適用對象\n"
            "第一條 本辦法依氣候變遷因應法規定訂定之。\n"
            "第二條 依本法應申報及繳納碳費之事業。\n"
            "第三條 本辦法自發布日施行。\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert — Legal articles should be the strategy, not Chinese outlines
        article_names = [c['metadata']['article'] for c in chunks]
        assert '第一條' in article_names
        assert '第二條' in article_names


# ──────────────────────────────────────────────
# Strategy 5: Fallback Paragraph Chunking
# ──────────────────────────────────────────────

class TestFallbackStrategy:
    """Tests for fallback paragraph-based chunking with overlap."""
    
    def test_falls_back_when_no_pattern_detected(self):
        """Text with no structural patterns should still be chunked."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=100)
        text = (
            "113年8月29日\n"
            "公告碳費三項子法，我國碳定價制度正式上路\n"
            "環境部今日公告碳費三項子法。\n"
            "碳費制度是經濟誘因工具。\n"
            "未來將結合公私部門資金推動減碳。\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert
        assert len(chunks) >= 1
        assert all(c['metadata']['article'] == 'General' for c in chunks)

    def test_overlap_between_chunks(self):
        """Fallback chunks should include overlapping text from previous chunk."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=80)
        # Build text with distinct paragraphs
        paragraphs = [
            f"Paragraph {i}: " + "x" * 30
            for i in range(5)
        ]
        text = "\n".join(paragraphs)
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert — at least 2 chunks
        assert len(chunks) >= 2
        # The last line of chunk N should appear at the start of chunk N+1 (overlap)
        if len(chunks) >= 2:
            # Check that there's some overlap content
            chunk0_lines = chunks[0]['text'].strip().split('\n')
            chunk1_text = chunks[1]['text']
            last_line_chunk0 = chunk0_lines[-1].strip()
            assert last_line_chunk0 in chunk1_text, (
                f"Expected overlap: last line of chunk 0 '{last_line_chunk0}' "
                f"should appear in chunk 1"
            )


# ──────────────────────────────────────────────
# Auto-detection / Priority
# ──────────────────────────────────────────────

class TestAutoDetection:
    """Tests for automatic strategy detection and priority ordering."""
    
    def test_legal_takes_priority_over_numbered(self):
        """第X條 should be detected even if numbered sections also exist."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = (
            "1.1 總則\n"
            "第一條\n"
            "本法為碳交易管理之基本法。\n"
            "第二條\n"
            "主管機關為環境部。\n"
            "第三條\n"
            "碳費徵收辦法。\n"
        )
        
        # Act
        chunks = chunker.split_text(text)
        
        # Assert — Legal articles should be detected, not numbered sections
        article_names = [c['metadata']['article'] for c in chunks]
        assert '第一條' in article_names
        assert '第二條' in article_names

    def test_default_max_chunk_size_is_250(self):
        """Default max_chunk_size should be 250."""
        # Arrange & Act
        chunker = ChunkStrategy()
        
        # Assert
        assert chunker.max_chunk_size == 250

    def test_metadata_passthrough(self):
        """Initial metadata should be preserved in all chunks."""
        # Arrange
        chunker = ChunkStrategy(max_chunk_size=2000)
        text = "Article 1\nSubject matter content.\nArticle 2\nScope content."
        metadata = {"source": "test.txt", "doc_type": "regulation"}
        
        # Act
        chunks = chunker.split_text(text, metadata)
        
        # Assert
        for chunk in chunks:
            assert chunk['metadata']['source'] == "test.txt"
            assert chunk['metadata']['doc_type'] == "regulation"

    def test_empty_text_returns_empty(self):
        """Empty or whitespace-only text should return an empty list."""
        # Arrange
        chunker = ChunkStrategy()
        
        # Act
        chunks_empty = chunker.split_text("")
        chunks_whitespace = chunker.split_text("   \n\n  ")
        
        # Assert
        assert chunks_empty == []
        assert chunks_whitespace == []
