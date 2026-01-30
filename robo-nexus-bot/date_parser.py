"""
Date parsing utilities for Robo Nexus Birthday Bot
Handles flexible date format parsing and validation
"""
import re
from datetime import date, datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class DateParser:
    """Handles parsing of various date formats for birthday registration"""
    
    # Supported date formats
    FORMATS = [
        r'^(\d{1,2})-(\d{1,2})$',           # MM-DD or M-D
        r'^(\d{1,2})/(\d{1,2})$',           # MM/DD or M/D
        r'^(\d{1,2})-(\d{1,2})-(\d{4})$',   # MM-DD-YYYY or M-D-YYYY
        r'^(\d{1,2})/(\d{1,2})/(\d{4})$',   # MM/DD/YYYY or M/D/YYYY
    ]
    
    @classmethod
    def parse_birthday(cls, date_string: str) -> Optional[date]:
        """
        Parse a birthday string into a date object
        
        Args:
            date_string: String representation of birthday
            
        Returns:
            date object if parsing successful, None otherwise
        """
        if not date_string or not isinstance(date_string, str):
            return None
        
        # Clean the input
        date_string = date_string.strip()
        
        try:
            # Try each format
            for format_pattern in cls.FORMATS:
                match = re.match(format_pattern, date_string)
                if match:
                    groups = match.groups()
                    
                    if len(groups) == 2:
                        # MM-DD or MM/DD format
                        month, day = map(int, groups)
                        year = datetime.now().year  # Use current year
                    else:
                        # MM-DD-YYYY or MM/DD/YYYY format
                        month, day, year = map(int, groups)
                    
                    # Validate the date
                    if cls._is_valid_date(month, day, year):
                        return date(year, month, day)
                    else:
                        logger.warning(f"Invalid date values: {month}/{day}/{year}")
                        return None
            
            # If no format matched
            logger.warning(f"No matching format for date string: {date_string}")
            return None
            
        except ValueError as e:
            logger.warning(f"Error parsing date '{date_string}': {e}")
            return None
    
    @classmethod
    def _is_valid_date(cls, month: int, day: int, year: int) -> bool:
        """
        Validate if the given month, day, year form a valid date
        
        Args:
            month: Month (1-12)
            day: Day (1-31)
            year: Year
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check basic ranges
            if not (1 <= month <= 12):
                return False
            
            if not (1 <= day <= 31):
                return False
            
            # Check if year is reasonable (not too far in past/future)
            current_year = datetime.now().year
            if not (1900 <= year <= current_year + 1):
                return False
            
            # Try to create the date (this will catch invalid combinations)
            date(year, month, day)
            return True
            
        except ValueError:
            return False
    
    @classmethod
    def format_birthday(cls, birthday) -> str:
        """
        Format a birthday date for display
        
        Args:
            birthday: Date object or string in MM-DD format
            
        Returns:
            Formatted string (e.g., "March 15")
        """
        # If it's already a date object, format it directly
        if isinstance(birthday, date):
            return birthday.strftime("%B %d")
        
        # If it's a string (from database), parse it first
        if isinstance(birthday, str):
            # Parse MM-DD format string
            parsed_date = cls.parse_birthday(birthday)
            if parsed_date:
                return parsed_date.strftime("%B %d")
            else:
                # Fallback: return the string as-is if parsing fails
                return birthday
        
        # Fallback for unexpected types
        return str(birthday)
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """
        Get list of supported date format examples
        
        Returns:
            List of format examples
        """
        return [
            "MM-DD (e.g., 03-15 for March 15)",
            "MM/DD (e.g., 03/15 for March 15)", 
            "MM-DD-YYYY (e.g., 03-15-1995)",
            "MM/DD/YYYY (e.g., 03/15/1995)"
        ]
    
    @classmethod
    def get_format_help_text(cls) -> str:
        """
        Get help text explaining supported formats
        
        Returns:
            Help text string
        """
        formats = cls.get_supported_formats()
        return "Supported date formats:\n" + "\n".join(f"• {fmt}" for fmt in formats)