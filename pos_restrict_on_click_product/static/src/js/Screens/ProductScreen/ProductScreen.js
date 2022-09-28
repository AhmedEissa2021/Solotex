odoo.define('pos_restrict_on_click_product.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen')
    const Registries = require('point_of_sale.Registries')
    const {posbus} = require('point_of_sale.utils')
    var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents
    const {useListener} = require('web.custom_hooks')
    const {useState} = owl.hooks
    const {Gui} = require('point_of_sale.Gui')

    const RetailProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                this._currentOrder = this.env.pos.get_order();
                if (this._currentOrder) {
                    this._currentOrder.orderlines.on('change', this._updateSummary, this);
                    this._currentOrder.orderlines.on('remove', this._updateSummary, this);
                    this._currentOrder.paymentlines.on('change', this._updateSummary, this);
                    this._currentOrder.paymentlines.on('remove', this._updateSummary, this);
                    this.env.pos.on('change:selectedOrder', this._updateCurrentOrder, this);
                }
            }




            async _clickProduct(event) {

            }

        }
    Registries.Component.extend(ProductScreen, RetailProductScreen);

    return RetailProductScreen;
});
