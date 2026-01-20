from srс.domain.entities.vending_machine import VendingMachine
from srс.domain.ports.vending_machine_repository import VendingMachineRepository
from srс.domain.entities.no_sales_report import NoSalesReport
from srс.services.no_sales_report_message_service import NoSalesReportMessageService
from srс.services.no_sales_report_service import NoSalesReportService


class CreateNoSalesReportMessage:
    def __init__(
            self,
            vending_machines_repository: VendingMachineRepository,
            report_service: NoSalesReportService,
            message_service: NoSalesReportMessageService,
            last_sale_days: int,
    ):
        self._vending_machines_repository = vending_machines_repository
        self._report_service = report_service
        self._message_service = message_service
        self._last_sale_days = last_sale_days

    async def execute(self, interval_hours: int) -> str:
        vending_machines: list[VendingMachine] = await self._vending_machines_repository.get_all()
        report: NoSalesReport = await self._report_service.create_report(
            vending_machines=vending_machines,
            interval_hours=interval_hours,
            last_sale_days=self._last_sale_days,
        )
        message: str = self._message_service.create_message(report)
        return message
