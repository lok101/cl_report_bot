from src.entities import MK
from src.enums import MKStatuses


class AlertService:
    @staticmethod
    def print_mk_without_sales(mks: list[MK], interval: int):
        without_sales = [mk for mk in mks if not mk.has_sale_in_selected_time_range(interval)]
        items = [mk for mk in without_sales if 'УГМК' not in mk.name]

        if items:
            print(f'Аппараты без продажи последние {interval} часа(ов):')
            for item in items:

                if item.last_sale_timestamp is None:
                    continue

                text = f'{item.name.ljust(50)} | {item.last_sale_timestamp.strftime("%d.%m.%Y %H:%M")}'
                print(text)
            print('\n')

    @staticmethod
    def print_mk_with_network_connection_error(mks: list[MK]):
        with_network_connection_error = [mk for mk in mks if mk.has_connection_error()]
        if with_network_connection_error:
            print('Аппараты без связи:')
            for item in with_network_connection_error:
                text = f'{item.name.ljust(50)} | {item.last_ping_timestamp.strftime("%d.%m.%Y %H:%M")}'
                print(text)
            print('\n')

    @staticmethod
    def print_snack_with_sales_unknown_product(mks: list[MK]):
        snacks = [mk for mk in mks if mk.is_snack()]
        items = [item for item in snacks if item.has_status(MKStatuses.SALE_UNKNOWN_PRODUCT)]
        if items:
            print('СНЭКи с неизвестными продажами:')
            for item in items:
                text = f'{item.name.ljust(50)}'
                print(text)
            print('\n')