"""
File Upload Handler Service
Supports document uploads for the knowledge base
"""

from typing import Dict, List, Optional, Any
from fastapi import UploadFile
import os
import hashlib
from datetime import datetime
import json
import PyPDF2
import docx
import io


class FileHandler:
    """
    Service for handling file uploads and processing
    Supports: PDF, DOCX, TXT, MD, JSON
    """
    
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md', '.json', '.csv'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        self.processed_files: Dict[str, Dict] = {}
    
    def _get_file_hash(self, content: bytes) -> str:
        """Generate hash for file deduplication"""
        return hashlib.md5(content).hexdigest()
    
    def _get_extension(self, filename: str) -> str:
        """Get file extension"""
        return os.path.splitext(filename)[1].lower()
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded file"""
        errors = []
        
        # Check extension
        ext = self._get_extension(file.filename)
        if ext not in self.ALLOWED_EXTENSIONS:
            errors.append(f"סוג קובץ לא נתמך: {ext}. סוגים נתמכים: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        # Check size
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        if len(content) > self.MAX_FILE_SIZE:
            errors.append(f"הקובץ גדול מדי. גודל מקסימלי: {self.MAX_FILE_SIZE // (1024*1024)}MB")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'size': len(content),
            'extension': ext
        }
    
    async def process_file(self, file: UploadFile, category: str = "general") -> Dict[str, Any]:
        """Process uploaded file and extract text content"""
        
        validation = await self.validate_file(file)
        if not validation['valid']:
            return {
                'success': False,
                'errors': validation['errors']
            }
        
        content = await file.read()
        file_hash = self._get_file_hash(content)
        
        # Check for duplicate
        if file_hash in self.processed_files:
            return {
                'success': False,
                'errors': ['קובץ זה כבר הועלה למערכת'],
                'duplicate': True,
                'existing_id': self.processed_files[file_hash]['id']
            }
        
        ext = validation['extension']
        
        try:
            # Extract text based on file type
            if ext == '.pdf':
                extracted_text = self._extract_pdf(content)
            elif ext == '.docx':
                extracted_text = self._extract_docx(content)
            elif ext == '.txt' or ext == '.md':
                extracted_text = content.decode('utf-8')
            elif ext == '.json':
                extracted_text = self._extract_json(content)
            elif ext == '.csv':
                extracted_text = self._extract_csv(content)
            else:
                extracted_text = content.decode('utf-8', errors='ignore')
            
            # Save file metadata
            file_id = f"file_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file_hash[:8]}"
            
            file_info = {
                'id': file_id,
                'filename': file.filename,
                'extension': ext,
                'size': len(content),
                'hash': file_hash,
                'category': category,
                'uploaded_at': datetime.now().isoformat(),
                'text_length': len(extracted_text)
            }
            
            self.processed_files[file_hash] = file_info
            
            # Save to disk
            save_path = os.path.join(self.upload_dir, f"{file_id}{ext}")
            with open(save_path, 'wb') as f:
                f.write(content)
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': file.filename,
                'extracted_text': extracted_text,
                'category': category,
                'metadata': file_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f'שגיאה בעיבוד הקובץ: {str(e)}']
            }
    
    def _extract_pdf(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            return "\n\n".join(text_parts)
        except Exception as e:
            raise Exception(f"שגיאה בקריאת PDF: {str(e)}")
    
    def _extract_docx(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc_file = io.BytesIO(content)
            doc = docx.Document(doc_file)
            
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            raise Exception(f"שגיאה בקריאת DOCX: {str(e)}")
    
    def _extract_json(self, content: bytes) -> str:
        """Extract text from JSON"""
        try:
            data = json.loads(content.decode('utf-8'))
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"שגיאה בקריאת JSON: {str(e)}")
    
    def _extract_csv(self, content: bytes) -> str:
        """Extract text from CSV"""
        try:
            text = content.decode('utf-8')
            lines = text.split('\n')
            return "\n".join(lines[:100])  # Limit to first 100 lines
        except Exception as e:
            raise Exception(f"שגיאה בקריאת CSV: {str(e)}")
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file information by ID"""
        for info in self.processed_files.values():
            if info['id'] == file_id:
                return info
        return None
    
    def list_files(self, category: Optional[str] = None) -> List[Dict]:
        """List all uploaded files"""
        files = list(self.processed_files.values())
        if category:
            files = [f for f in files if f['category'] == category]
        return files
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file"""
        for hash_key, info in list(self.processed_files.items()):
            if info['id'] == file_id:
                # Delete from disk
                save_path = os.path.join(self.upload_dir, f"{file_id}{info['extension']}")
                if os.path.exists(save_path):
                    os.remove(save_path)
                
                # Remove from memory
                del self.processed_files[hash_key]
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get file upload statistics"""
        files = list(self.processed_files.values())
        total_size = sum(f['size'] for f in files)
        
        categories = {}
        for f in files:
            cat = f['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'categories': categories,
            'file_types': {f['extension']: 1 for f in files}
        }


# Global instance
file_handler = FileHandler()
