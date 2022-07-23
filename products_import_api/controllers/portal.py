from odoo import http, _, fields
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
import json


class PortalProduct(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'products_count' in counters:
            products_count = request.env['product.template'].search_count(self._get_products_domain(partner))
            values['products_count'] = products_count
        return values

    # ------------------------------------------------------------
    # My Products
    # ------------------------------------------------------------

    def _request_get_page_view_values(self, request, access_token, **kwargs):
        values = {
            'page_name': 'request',
            'request': request,
        }
        return self._get_page_view_values(request, access_token, values, 'my_products_history', False, **kwargs)

    def _get_products_domain(self, partner):
        
        return []

    def _get_pricelist_domain(self, partner):
        return [
            ('pricelist_id', '=' , partner.property_product_pricelist.id)
        ]

    def action_to_confirm(self):
        print('nothing to do')
        return

    @http.route(['/my/products', '/my/products/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_products(self, page=1, sortby=None, filterby=None, searchval=None, sale_request_id=None, **kw):
        values = self._prepare_portal_layout_values()
        Products = request.env['product.template'].sudo()
        partner = request.env.user.partner_id

        domain = self._get_products_domain(partner)

        searchbar_sortings = {
            'name': {'label': _('Reference'), 'order': 'name desc'},
            # 'status': {'label': _('Status'), 'order': 'status'},
        }
        # default sort by order
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            # 'draft': {'label': _('Status: Draft'), 'domain': [('status', '=', ('draft'))]},
            # 'to_confirm': {'label': _('Status: To confirm'), 'domain': [('status', '=', ('to_confirm'))]},
            # 'confirmed': {'label': _('Status: Confirmed'), 'domain': [('status', '=', ('confirmed'))]},
            # 'approved': {'label': _('Status: Approved'), 'domain': [('status', '=', ('approved'))]},
            # 'not_delivery': {'label': _('Delivery: None'), 'domain': [('fulfilment_status', '=', ('not_delivery'))]},
            # 'in_prepare': {'label': _('Delivery: In Prepare'), 'domain': [('fulfilment_status', '=', ('in_prepare'))]},
            # 'partial_ready': {'label': _('Delivery: Partial Ready'), 'domain': [('fulfilment_status', '=', ('partial_ready'))]},
            # 'ready': {'label': _('Delivery: Ready'), 'domain': [('fulfilment_status', '=', ('ready'))]},
            # 'partial_done': {'label': _('Delivery: Partial Done'), 'domain': [('fulfilment_status', '=', ('partial_done'))]},
            # 'deliveried': {'label': _('Delivery: Done'), 'domain': [('fulfilment_status', '=', ('deliveried'))]},
            # 'cancel': {'label': _('Delivery: Cancel'), 'domain': [('fulfilment_status', '=', ('cancel'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # filter by search values
        if searchval:
            searchbar_values = [('name', 'ilike', searchval)]
            domain += searchbar_values
            
        # count for pager
        products_count = Products.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/products",
            url_args={'sortby': sortby},
            total=products_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        products = Products.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_products_history'] = products.ids[:100]

        # # Check for update to confirm request
        # if sale_request_id:
        #     confirm_sale_request = Products.browse(sale_request_id)
        #     if confirm_sale_request.exists():
        #         confirm_sale_request.write({'status': 'confirmed'})
        #     else:
        #         return f'<h1>Error</h1>\nSale request {confirm_sale_request.name} have been confirmed or cancel'
        
        values.update({
            'products': products,
            'page_name': 'products',
            'pager': pager,
            'default_url': '/my/products',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'searchval': searchval,
        })
        return request.render("products_import_api.portal_my_products", values)

    @http.route(['/my/products/<int:request_id>'], type='http', auth="public", website=True)
    def portal_my_request_detail(self, request_id, access_token=None, report_type=None, download=False, **kw):
        # try:
        #     request_sudo = self._document_check_access('req.move', request_id, access_token)
        # except (AccessError, MissingError):
        #     return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #     return self._show_report(model=request_sudo, report_type=report_type, report_ref='account.account_products', download=download)
        return
        values = self._request_get_page_view_values(request_sudo, access_token, **kw)
        return request.render("products_import_api.portal_request_page", values)

    # ------------------------------------------------------------
    # My Home
    # ------------------------------------------------------------

    def details_form_validate(self, data):
        error, error_message = super(PortalRequest, self).details_form_validate(data)
        # prevent VAT/name change if products exist
        partner = request.env['res.users'].browse(request.uid).partner_id
        if not partner.can_edit_vat():
            if 'vat' in data and (data['vat'] or False) != (partner.vat or False):
                error['vat'] = 'error'
                error_message.append(_('Changing VAT number is not allowed once products have been issued for your account. Please contact us directly for this operation.'))
            if 'name' in data and (data['name'] or False) != (partner.name or False):
                error['name'] = 'error'
                error_message.append(_('Changing your name is not allowed once products have been issued for your account. Please contact us directly for this operation.'))
            if 'company_name' in data and (data['company_name'] or False) != (partner.company_name or False):
                error['company_name'] = 'error'
                error_message.append(_('Changing your company name is not allowed once products have been issued for your account. Please contact us directly for this operation.'))
        return error, error_message

    @http.route(['/my/products/new'], type='http', auth="user", website=True)
    def portal_my_request_create(self,page=1, access_token=None, report_type=None, download=False,search = None, **kw):
        values = self._prepare_portal_layout_values()
        Products = request.env['product.template'].sudo()

        product_domain = []
       
        # count for pager
        products_count = Products.search_count(product_domain)
        product_pager = portal_pager(
            url= "/my/products/new",
            total = products_count,
            page = page,
            step= self._items_per_page,
        )

        products = Products.search(product_domain)
        request.session['my_products_history'] = products.ids[:100]

        values.update({
            'products': products,
            'page_name': 'placerequest',
            'pager': product_pager,
            'default_url': '/my/products/new',
            'search': search,
        })
        return request.render("products_import_api.portal_my_products_create", values)

    @http.route('/my/products/SR', type='json', auth="user")
    def portal_json_create(self,**kw):
        salesperson_id = kw.get('salesperson')
        user_id = kw.get('retailer')
        products = kw.get('pd_line_lst')
        due_date = kw["due_date"]
        partner_id = request.env['res.users'].sudo().browse(user_id).partner_id.id
        if (partner_id):
            new_sr=request.env['product.template'].sudo().create({
                'retailer_id': partner_id,
                'salesperson_id': salesperson_id,
                'due_date_customer': fields.Date.from_string(due_date)
            })
        return '/my/products'

    @http.route('/my/getproduct', type='json', auth="user")
    def portal_get_product_info(self,**kw):
        product_id = kw.get('product_id')
        user_id = kw.get('user_id')
        quantity = kw.get('quantity')
        partner = request.env['res.users'].sudo().browse(user_id).partner_id
        partner_id = partner.id
        pricelist = partner.property_product_pricelist
        if (product_id and partner_id):
            if not quantity:
                quantity = 1
            product = request.env['product.template'].sudo().browse(product_id)
            price = pricelist.get_product_price(product=product, quantity=quantity, partner=partner_id)
            return {
                "id":product.id,
                "name": product.display_name,
                "price":product.lst_price,
                "fact_price": price,
                "crv":product.crv_cost,
                "quantity": quantity,
                "uom_id":product.uom_id.id,
                "uom_name":product.uom_id.name,
                "currency_id":product.currency_id.id,
                "currency_name":product.currency_id.name,
                "currency_symbol": product.currency_id.symbol,
            }
        return dict()
   