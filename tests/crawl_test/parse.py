import sys
sys.path.append('/Users/jamesenh/projects/github/crawl4ai')
from crawl4ai.web_crawler import WebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import Union
import json


class FieldItem(BaseModel):
    name: str = Field(..., description="Name of the field.")
    value: Union[str, list[str], list[int], list[float], int, float, bool, None] = Field(..., description="Value of the field.")
    score: float = Field(..., description="The credibility of the field, percentage value, maximum 1.0")

class Hospital(BaseModel):
    name: str = Field(..., description="Name of the hospital.")
    address: str = Field(..., description="Address of the hospital.")
    phone: list[str] = Field(..., description="Phone number of the hospital.")
    department_number: int = Field(..., description="Number of departments in the hospital.")
    doctor_number: int = Field(..., description="Number of doctors in the hospital.")
    introduction: str = Field(..., description="Introduction of the hospital.")
    url: str = Field(..., description="URL of the hospital.")
    # 属性，是否公立
    public: bool = Field("Unknown", description="Whether the hospital is public or not.")
    # 医院等级
    level: str = Field("Unknown", description="Level of the hospital.")
    # 医院省份
    province: str = Field("Unknown", description="Province of the hospital.")
    # 医院城市
    city: str = Field("Unknown", description="City of the hospital.")
    # 医院区域
    area: str = Field("Unknown", description="Area of the hospital.")
    # 创办时间
    established_time: str = Field("Unknown", description="Established time of the hospital.")
    # 医院类型
    hospital_type: str = Field("Unknown", description="Type of the hospital, only choose one from '综合医院', '专科医院', '中医医院', '民族医院', '军队医院', '基层医院', '其他'.")
    
class Department(BaseModel):
    name: str = Field(..., description="Name of the department.")
    hospital_name: str = Field(..., description="Name of the hospital where the department works.")
    doctor_number: int = Field(..., description="Number of doctors in the department.")
    url: str = Field(..., description="URL of the department.")

class Doctor(BaseModel):
    name: str = Field(..., description="Name of the doctor.")
    hospital_name: str = Field(..., description="Name of the hospital where the doctor works.")
    department_name: str = Field(..., description="Name of the department where the doctor works.")
    url: str = Field(..., description="URL of the doctor.")
    # 职位
    position: str = Field(..., description="Position of the doctor.")

class Item(BaseModel):
    info_type: str = Field(..., description="Type of information extracted, such as doctor, hospital, or department.")
    item: Union[Doctor, Hospital, Department] = Field(..., description="Doctor or hospital information extracted.")

url = "https://y.dxy.cn/hospital/?page=1"

crawler = WebCrawler(verbose=True)

result = crawler.run(
    url, 
    warmup=False, 
    bypass_cache=True,
    extraction_strategy=LLMExtractionStrategy(
        provider="openai/LinkAI-4o-mini",
        base_url="***",
        api_token="***",
        schema=Item.model_json_schema(),
        extraction_type="schema",
        instruction="从抓取的内容中提取跟医生、医院、科室相关的信息,如果必填字段没有提取到则填空字符，信息描述尽量使用中文",
        post_process=True
    )
)

# 解析结果
res = json.loads(result.extracted_content)
with open('test/data/result.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=4)

with open('test/data/links_internal.json', 'w', encoding='utf-8') as f:
    json.dump(result.links.get("internal", []), f, ensure_ascii=False, indent=4)

with open('test/data/links_external.json', 'w', encoding='utf-8') as f:
    json.dump(result.links.get("external", []), f, ensure_ascii=False, indent=4)
