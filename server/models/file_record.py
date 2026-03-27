from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from datetime import datetime
from typing import Literal, Optional

class BaseConfigModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

class BorrowerFileRecord(BaseConfigModel):
    id: str
    borrower_id: str
    file_name: str
    file_path: str
    classification: Optional[Literal["w2", "bank_statement", "1099", "institution_report"]] = None
    status: Optional[Literal["stripe", "plaid", "shopify", "paypal", "amazon_seller", "upwork/fiverr", "bank", "other"]] = None
    created_at: datetime