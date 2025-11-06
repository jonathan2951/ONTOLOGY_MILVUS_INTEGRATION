# examples from the notebook `create_tables_collection.ipynb example.md`

## semantic match

```py
query: str = "stock_iq"
query_vector = embed_text(texts=query)

search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 128}
}
top_k = 5


# Single vector search
res = client.search(
    collection_name=collection_name,
    data=query_vector,
    search_params=search_params,
    limit=top_k,
    output_fields=["text", "name"]
)

for i, hits in enumerate(res):
    for hit in hits:
        print(f"name:{hit.entity.get('name')}")
        print(f"distance: {hit.get('distance')}")
        print("")

# name:group_iii.silver.stock_iq_forecast_2024_2025_xlsx_sheet
# distance: 0.5004482865333557

# name:group_iii.silver.stock_iq_lost_sales_xlsx_sheet
# distance: 0.42270272970199585

# name:group_iii.silver.insitestatus
# distance: 0.3762144446372986

# name:group_iii.silver.initemstats
# distance: 0.372540146112442

# name:group_iii.silver.inturnovercalcitem
# distance: 0.367465615272522
```

## direct filtering
- https://milvus.io/docs/boolean.md

```py
filter = "name == 'group_iii.silver.initemstats'"
res2 = client.query(
    collection_name=collection_name,
    filter=filter,
    output_fields=["text", "name", "id"],
)
```

```py
# here we see that only 1 document has been retrieved since it is an exact match
res2, len(res2)
#(data: ["{'id': 278, 'text': 'table name:group_iii.silver.initemstats\\ntable description:  It covers data from the years 2023 to 2025. The table contains information about inventory items, including details such as CompanyID, InventoryID, SiteID, and various cost metrics. This data is valuable for tracking inventory levels, costs, and site-specific information, aiding in inventory management and financial analysis.\\ntable_primary_keys:CompanyID,InventoryID,SiteID\\ncolumns available:CompanyID,InventoryID,SiteID,QtyOnHand,TotalCost,MinCost,MaxCost,LastCost,LastCostDate,LastPurchaseDate,ValMethod,tstamp\\ncategory: Procurement & Inventory', 'name': 'group_iii.silver.initemstats'}"], extra_info: {}, 1)
```

- when filtering on categories, because 1 category contains many tables, we got several records
```py
filter = "category == 'Procurement & Inventory'"
res3 = client.query(
    collection_name=collection_name,
    filter=filter,
    output_fields=["name", "id", "category"],
)

[x for x in res3]

# [{'name': 'group_iii.silver.group_iii_purchase_xlsx_g_3_p_order',
#   'id': 0,
#   'category': 'Procurement & Inventory'},
#  {'name': 'group_iii.silver.initemsitehistday',
#   'id': 1,
#   'category': 'Procurement & Inventory'},
#  ...
#   'id': 746,
#   'category': 'Procurement & Inventory'}]
```

## partial filtering
- SQL like expression
- https://milvus.io/docs/boolean.md
```py
filter_expression = "name like \"%initem%\" " 

res4 = client.query(
    collection_name=collection_name,
    filter=filter_expression,
    output_fields=["text", "name", "id", "category"],
)

for x in res4:
    print(f"{x.get("name")}", {x.get("category")})

# group_iii.silver.initemsitehistday {'Procurement & Inventory'}
# group_iii.silver.initemcustsalesstats {'Procurement & Inventory'}
# group_iii.silver.initemclass {'Procurement & Inventory'}
# group_iii.silver.initemcost {'Procurement & Inventory'}
# group_iii.silver.initemsite {'Procurement & Inventory'}
# group_iii.silver.initemstats {'Procurement & Inventory'}
# group_iii.silver.initemclassrep {'Procurement & Inventory'}
# group_iii.silver.initemcategory {'Sales'}
# group_iii.silver.initemplan {'Procurement & Inventory'}
# group_iii.silver.initemsitehistbycostcenterd {'Procurement & Inventory'}
# group_iii.silver.initemrep {'Procurement & Inventory'}
# group_iii.silver.initemsaleshist {'Procurement & Inventory'}
# group_iii.silver.initemcosthist {'Procurement & Inventory'}
# group_iii.silver.initemxref {'Procurement & Inventory'}
# group_iii.silver.initemsitehist {'Procurement & Inventory'}
# group_iii.silver.initembox {'Procurement & Inventory'}
# group_iii.silver.initemclasscurysettings {'Procurement & Inventory'}
# group_iii.silver.initemsitehistd {'Procurement & Inventory'}
# group_iii.silver.initemcustsaleshist {'Procurement & Inventory'}
# group_iii.silver.initemsaleshistd {'Procurement & Inventory'}
```

## # phrase matching
- search for documents containing your query terms as an exact phrase
- https://milvus.io/docs/phrase-match.md
- Phrase match lets you search for documents containing your query terms as an exact phrase. By default, the words must appear in the same order and directly adjacent to one another. For example, a query for “robotics machine learning” matches text like “…typical robotics machine learning models…”, where the words “robotics”, “machine”, and “learning” appear in sequence with no other words between them.
- The slop parameter controls the maximum number of positions allowed between matching tokens

```py
filter = "PHRASE_MATCH(text, 'inventory levels')"

res5 = client.query(
    collection_name=collection_name,
    filter=filter,
    output_fields=["id", "text", "name", "category"]
)

[x for x in res5]

# [{'id': 0,
#   'text': 'table name:group_iii.silver.group_iii_purchase_xlsx_g_3_p_order\ntable description:  It covers data from various dates and contains information about purchase orders, including details such as order number, date, vendor, status, and quantities. This data is valuable for tracking purchase orders, analyzing vendor performance, and managing inventory levels.\ntable_primary_keys:OrderNbr,LineNbr\ncolumns available:Type,OrderNbr,Date,PromisedOn,Vendor,VendorName,Status,TotalOrderQty,OpenQuantity,CreatedBy,InventoryID,Description,Description_2,ShipTo,AccountName,OrderQty_2,QtyOnReceipts,ExtCost,UnitCost,LineNbr,BranchID,EntityType\ncategory: Procurement & Inventory',
#   'name': 'group_iii.silver.group_iii_purchase_xlsx_g_3_p_order',
#   'category': 'Procurement & Inventory'},
#  {'id': 1,
#   'text': 'table name:group_iii.silver.initemsitehistday\ntable description:  It covers data from the years 2023 to 2025. The table contains information about inventory movements, including details such as company ID, inventory ID, site ID, location ID, and various quantity metrics. This data is valuable for tracking inventory levels, analyzing stock movements, and optimizing supply chain operations.\ntable_primary_keys:CompanyID,InventoryID,SubItemID,SiteID,LocationID,SDate\ncolumns available:CompanyID,InventoryID,SubItemID,SiteID,LocationID,SDate,BegQty,EndQty,QtyReceived,QtyIssued,QtySales,QtyCreditMemos,QtyDropShipSales,QtyTransferIn,QtyTransferOut,QtyAssemblyIn,QtyAssemblyOut,QtyAdjusted,QtyDebit,QtyCredit,tstamp\ncategory: Procurement & Inventory',
#   'name': 'group_iii.silver.initemsitehistday',
#   'category': 'Procurement & Inventory'},
#   ...
#  ]
```