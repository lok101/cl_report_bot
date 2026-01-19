from typing import Optional

from src.entities import MK
from src.enums import MKStatuses


class AlertService:
    @staticmethod
    def print_mk_without_sales(mks: list[MK], interval: int):
        text: Optional[str] = AlertService._format_mk_without_sales(mks, interval)
        if text:
            print(text)
            print('\n')

    @staticmethod
    def print_mk_with_network_connection_error(mks: list[MK]):
        text: Optional[str] = AlertService._format_mk_with_network_connection_error(mks)
        if text:
            print(text)
            print('\n')

    @staticmethod
    def print_snack_with_sales_unknown_product(mks: list[MK]):
        text: Optional[str] = AlertService._format_snack_with_sales_unknown_product(mks)
        if text:
            print(text)
            print('\n')

    @staticmethod
    def build_report(mks: list[MK], interval: int) -> str:
        sections: list[str] = []

        without_sales: Optional[str] = AlertService._format_mk_without_sales(mks, interval)
        if without_sales:
            sections.append(without_sales)

        with_network_connection_error: Optional[str] = AlertService._format_mk_with_network_connection_error(mks)
        if with_network_connection_error:
            sections.append(with_network_connection_error)

        snacks_with_unknown_sales: Optional[str] = AlertService._format_snack_with_sales_unknown_product(mks)
        if snacks_with_unknown_sales:
            sections.append(snacks_with_unknown_sales)

        return "\n\n".join(sections)

    @staticmethod
    def _format_mk_without_sales(mks: list[MK], interval: int) -> Optional[str]:
        without_sales: list[MK] = [mk for mk in mks if not mk.has_sale_in_selected_time_range(interval)]
        items: list[MK] = [mk for mk in without_sales if 'УГМК' not in mk.name]

        if not items:
            return None

        lines: list[str] = [f'\nАппараты без продажи последние {interval} часа(ов):\n']
        for item in items:
            if item.last_sale_timestamp is None:
                continue

            line: str = f'{item.name.ljust(50)} | {item.last_sale_timestamp.strftime("%d.%m.%Y %H:%M")}'
            lines.append(line)

        if len(lines) == 1:
            return None

        return "\n".join(lines)

    @staticmethod
    def _format_mk_with_network_connection_error(mks: list[MK]) -> Optional[str]:
        with_network_connection_error: list[MK] = [mk for mk in mks if mk.has_connection_error()]
        if not with_network_connection_error:
            return None

        lines: list[str] = ['Аппараты без связи:']
        for item in with_network_connection_error:
            line: str = f'{item.name.ljust(50)} | {item.last_ping_timestamp.strftime("%d.%m.%Y %H:%M")}'
            lines.append(line)
        return "\n".join(lines)

    @staticmethod
    def _format_snack_with_sales_unknown_product(mks: list[MK]) -> Optional[str]:
        snacks: list[MK] = [mk for mk in mks if mk.is_snack()]
        items: list[MK] = [item for item in snacks if item.has_status(MKStatuses.SALE_UNKNOWN_PRODUCT)]
        if not items:
            return None

        lines: list[str] = ['СНЭКи с неизвестными продажами:']
        for item in items:
            line: str = f'{item.name.ljust(50)}'
            lines.append(line)
        return "\n".join(lines)