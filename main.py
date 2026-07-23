import os
import requests
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(
    title="BR-KYC Agent - XDC Oracle Service",
    description="Fiscal validation oracle for Brazilian CNPJs operating on the XDC Network.",
    version="1.0.0"
)

SERVICE_PRICE_USDC = 0.02

class CNPJResponse(BaseModel):
    cnpj: str
    company_name: str
    trading_name: str
    status: str
    tax_status_valid: bool
    price_charged_usdc: float

@app.get("/")
def read_root():
    return {
        "service": "BR-KYC Agent",
        "provider": "Celeris Digital Asset",
        "network": "XDC Network",
        "status": "Active",
        "price_per_query": f"${SERVICE_PRICE_USDC} USDC"
    }

@app.get("/v1/validate/{cnpj}", response_model=CNPJResponse)
def validate_cnpj(cnpj: str):
    clean_cnpj = "".join(filter(str.isdigit, cnpj))
    
    if len(clean_cnpj) != 14:
        raise HTTPException(status_code=400, detail="Invalid CNPJ format. Must contain 14 digits.")
    
    url = f"https://brasilapi.com.br/api/cnpj/v1/{clean_cnpj}"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="CNPJ not found or service unavailable.")
    
    data = response.json()
    is_active = data.get("descricao_situacao_cadastral", "").upper() == "ATIVA"
    
    return {
        "cnpj": clean_cnpj,
        "company_name": data.get("razao_social", ""),
        "trading_name": data.get("nome_fantasia", "") or data.get("razao_social", ""),
        "status": data.get("descricao_situacao_cadastral", "UNKNOWN"),
        "tax_status_valid": is_active,
        "price_charged_usdc": SERVICE_PRICE_USDC
    }
