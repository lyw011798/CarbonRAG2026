import pathlib
from typing import Dict, Type
from .base import DocumentProcessor

class ProcessorFactory:
    """Factory to resolve DocumentProcessor implementations by file extension."""
    
    _registry: Dict[str, Type[DocumentProcessor]] = {}
    
    @classmethod
    def register(cls, extension: str, processor_cls: Type[DocumentProcessor]) -> None:
        """
        Register a DocumentProcessor class for a specific file extension.
        
        Args:
            extension: File extension (e.g., '.pdf', 'txt').
            processor_cls: The processor class extending DocumentProcessor.
        """
        ext = extension.lower()
        if not ext.startswith("."):
            ext = "." + ext
        cls._registry[ext] = processor_cls
        
    @classmethod
    def get_processor(cls, file_path: str | pathlib.Path, **kwargs) -> DocumentProcessor:
        """
        Get an instantiated processor suitable for the given file path.
        
        Args:
            file_path: Path to the document.
            **kwargs: Extra arguments to optionally pass to the processor constructor.
            
        Returns:
            An instance of a corresponding DocumentProcessor subclass.
            
        Raises:
            ValueError: If no processor is registered for the extension.
        """
        path = pathlib.Path(file_path)
        ext = path.suffix.lower()
        
        processor_cls = cls._registry.get(ext)
        if not processor_cls:
            raise ValueError(f"No document processor registered for extension '{ext}'")
            
        return processor_cls(**kwargs)
