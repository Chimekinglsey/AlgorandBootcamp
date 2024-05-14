from algopy import Asset, ARC4Contract, arc4, itxn, gtxn, Txn, UInt64, Global


class SmartCon(ARC4Contract):
    """SmartCon contract."""
    asset_id: UInt64
    unit_price: UInt64


    @arc4.abimethod(allow_actions=["NoOp"], create="require")
    def create_app(self, asset: Asset, unit_price: UInt64) -> None:
        """Create an application"""
        self.asset_id = asset.id
        self.unit_price = unit_price

    @arc4.abimethod
    def set_price(self, new_unit_price:UInt64) -> None:
        """Set new unit price for the application"""
        assert Txn.sender == Global.creator_address # "Only creator can set price"
        assert new_unit_price > 0
        self.unit_price = new_unit_price

    @arc4.abimethod
    def opt_in(self, mbr_txn: gtxn.PaymentTransaction) -> None:
        """Opt-in to the application to avoid spam"""
        assert not Global.caller_application_address.is_opted_in(Asset(self.asset_id))
        assert mbr_txn.amount == Global.min_balance + Global.asset_opt_in_min_balance
        assert mbr_txn.receiver == Global.current_application_address

        itxn.AssetTransfer(
            xfer_asset = self.asset_id,
            sender=Global.current_application_address,
            asset_receiver=Txn.sender,
            asset_amount = 0
        ).submit()


    @arc4.abimethod
    def buy_asset(self, buy_txn: gtxn.PaymentTransaction, quantity: UInt64) -> None:
        """Buy Asset"""
        assert self.unit_price != UInt64(0)
        assert buy_txn.sender == Txn.sender
        assert buy_txn.amount == self.unit_price * quantity
        assert buy_txn.receiver == Global.current_application_address


        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            sender=Global.current_application_address,
            asset_receiver=Txn.sender,
            asset_amount=quantity
        ).submit()

    @arc4.abimethod(allow_actions=["DeleteApplication"])
    def delete_app(self) -> None:
        """Delete the application"""
        assert Txn.sender == Global.creator_address

        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            sender=Global.current_application_address,
            asset_receiver=Global.creator_address,
            asset_amount=0,
            asset_close_to=Global.creator_address
        ).submit()

        itxn.Payment(
            amount=0,
            sender=Global.current_application_address,
            receiver=Global.creator_address,
            close_remainder_to=Global.creator_address
        ).submit()
