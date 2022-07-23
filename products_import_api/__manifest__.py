# Copyright © 2022 Novobi, LLC
# See LICENSE file for full copyright and licensing details.
{
    "name": "Products Import Portal",
    "version": "15.0.0",
    "category": "Tools",
    "website": "https://novobi.com",
    "author": "Nguyen Vi, Novobi, LLC",
    "depends": [
        "base", "website_sale", "product", "portal"
    ],
     "excludes": [],
    "data": [
        # ============================== DATA =================================
        
        # ============================== VIEWS ================================
        "views/product_portal_templates.xml",
        "views/product_import_views.xml",
        # ============================== SECURITY ================================

        # ============================== REPORT =============================

        # ============================== WIZARDS =============================  
    ],
    "application": True,
    "installable": True,
}
