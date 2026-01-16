import streamlit as st
import requests
import uuid
import json
import pandas as pd

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="E-Commerce Admin", layout="wide")

# --- Helper Functions ---
def get_products(params=None):
    try:
        response = requests.get(f"{API_BASE_URL}/products", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return None

def create_product(data):
    try:
        response = requests.post(f"{API_BASE_URL}/products", json=data)
        return response
    except Exception as e:
        st.error(f"Error creating product: {e}")
        return None

def update_product(product_id, data):
    try:
        # Note: Backend uses singular /product/{id} for PATCH
        response = requests.patch(f"{API_BASE_URL}/product/{product_id}", json=data)
        return response
    except Exception as e:
        st.error(f"Error updating product: {e}")
        return None

def delete_product(product_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/products/{product_id}")
        return response
    except Exception as e:
        st.error(f"Error deleting product: {e}")
        return None

# --- UI Components ---
def sidebar_nav():
    st.sidebar.title("Navigation")
    return st.sidebar.radio("Go to", ["Home", "Product Catalog", "Add New Product"])

def home_page():
    st.title("Welcome to FastAPI E-Commerce")
    
    # Check API Health
    try:
        res = requests.get(f"{API_BASE_URL}/")
        if res.status_code in [200, 202]:
            data = res.json()
            st.success("Backend is Connected! 🟢")
            st.json(data)
        else:
            st.warning(f"Backend returned status: {res.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to Backend. Is uvicorn running?")

def product_catalog():
    st.title("Product Catalog")

    # Filters
    with st.expander("Search & Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_name = st.text_input("Search by Name")
        with col2:
            category = st.selectbox("Category", ["All", "laptops", "mobiles", "accessories", "electronics"])
        with col3:
            max_price = st.number_input("Max Price", min_value=0.0, value=0.0, step=100.0)
        with col4:
            sort_order = st.selectbox("Sort Order", ["asc", "desc"])
    
    # Fetch Data
    params = {"limit": 100, "order": sort_order}
    if search_name: params["name"] = search_name
    if category != "All": params["category"] = category
    if max_price > 0: params["price"] = max_price

    data = get_products(params)
    
    if data and "items" in data and data["items"]:
        items = data["items"]
        st.markdown(f"**Found {data['total']} products**")

        for product in items:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 4, 2])
                
                with c1:
                    if product.get("image_urls") and len(product["image_urls"]) > 0:
                        st.image(product["image_urls"][0], width=100)
                    else:
                        st.text("No Image")
                
                with c2:
                    st.subheader(product.get("name", "Unknown Product"))
                    st.caption(f"Category: {product.get('category')} | Brand: {product.get('brand')}")
                    st.write(product.get("description", "")[:100] + "...")
                    
                    # Tags
                    tags = product.get("tags")
                    if tags:
                        st.write("Labels: " + ", ".join([f"`{t}`" for t in tags]))
                
                with c3:
                    price = product.get("price", 0)
                    discount = product.get("discount_percent", 0)
                    final_price = product.get("final_price", price)
                    
                    if discount > 0:
                        st.markdown(f"~~₹{price}~~ **₹{final_price}**")
                        st.markdown(f"🔥 {discount}% OFF")
                    else:
                        st.markdown(f"**₹{price}**")
                    
                    st.markdown(f"⭐ {product.get('rating', 0)}/5")
                    st.markdown(f"📦 Stock: {product.get('stock')}")
                    
                    # Actions
                    ac1, ac2 = st.columns(2)
                    if ac1.button("🗑️ Delete", key=f"del_{product['id']}"):
                        res = delete_product(product['id'])
                        if res and res.status_code == 200:
                            st.success("Deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
                    
                    # We can't easily do a full edit modal without more complex state defaults
                    # but we can do a simple stock update or price update here if needed.
                    # For now, delete is the primary action.

    else:
        st.info("No products found.")

def add_product_page():
    st.title("Add New Product")
    
    with st.form("new_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", placeholder="Product Name (6-80 chars)")
            sku = st.text_input("SKU", placeholder="e.g. ITEM-001 (Must end with -3digits)")
            category = st.selectbox("Category", ["mobiles", "laptops", "accessories", "electronics"])
            brand = st.text_input("Brand", placeholder="Xiaomi, Apple, etc.")
            price = st.number_input("Price (INR)", min_value=1.0, step=100.0)
            discount = st.number_input("Discount (%)", min_value=0, max_value=90, step=1)
        
        with col2:
            description = st.text_area("Description", placeholder="Short description (max 200 chars)")
            stock = st.number_input("Stock", min_value=0, step=1)
            rating = st.number_input("Rating (0-5)", min_value=0.0, max_value=5.0, step=0.1)
            is_active = st.checkbox("Is Active", value=True)
            tags_str = st.text_input("Tags (comma separated)", placeholder="gaming, budget, best-seller")
            img_url = st.text_input("Image URL", value="https://via.placeholder.com/150")

        st.subheader("Dimensions & Seller Info")
        d1, d2, d3 = st.columns(3)
        with d1: length = st.number_input("Length (cm)", min_value=0.1, value=10.0)
        with d2: width = st.number_input("Width (cm)", min_value=0.1, value=5.0)
        with d3: height = st.number_input("Height (cm)", min_value=0.1, value=2.0)

        s1, s2, s3 = st.columns(3)
        with s1: seller_name = st.text_input("Seller Name", value="Official Store")
        with s2: seller_email = st.text_input("Seller Email", value="contact@lenovostore.in", help="Must be allowed domain like lenovostore.in")
        with s3: seller_website = st.text_input("Seller Website", value="https://lenovostore.in")

        submitted = st.form_submit_button("Create Product")
        
        if submitted:
            # Construct Payload
            # NOTE: ID is required by Pydantic schema even if backend ignores it
            dummy_id = str(uuid.uuid4())
            dummy_seller_id = str(uuid.uuid4())
            
            tags_list = [t.strip() for t in tags_str.split(",")] if tags_str else []
            
            payload = {
                "id": dummy_id,
                "sku": sku,
                "name": name,
                "description": description,
                "category": category,
                "brand": brand,
                "price": price,
                "currency": "INR",
                "discount_percent": discount,
                "stock": stock,
                "is_active": is_active,
                "rating": rating,
                "tags": tags_list,
                "image_urls": [img_url],
                "dimensions_cm": {
                    "length": length,
                    "width": width,
                    "height": height
                },
                "seller": {
                    "id": dummy_seller_id,
                    "name": seller_name,
                    "email": seller_email,
                    "website": seller_website
                },
                "created_at": "2024-01-01T00:00:00" # Placeholder, backend might override or just accept
            }
            
            res = create_product(payload)
            if res:
                if res.status_code == 201:
                    st.success("Product Created Successfully!")
                    st.json(res.json())
                else:
                    st.error(f"Failed to create: {res.text}")

# --- Main App Logic ---
page = sidebar_nav()

if page == "Home":
    home_page()
elif page == "Product Catalog":
    product_catalog()
elif page == "Add New Product":
    add_product_page()
