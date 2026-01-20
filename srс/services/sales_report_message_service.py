from srс.domain.entities.sales_analyze_report import SalesAnalyzeReport


class SalesReportMessageService:
    def create_message(self, sales_report: SalesAnalyzeReport) -> str:
        if not sales_report.items:
            return ""

        lines: list[str] = ["\nАппараты с падением продаж:"]
        for item in sales_report.items:
            percent: int = round(item.deviation_ratio * 100)
            line: str = f"{item.vending_machine.name}\nПадение продаж за вчера на {percent}%"
            lines.append(line)

        message: str = "\n\n".join(lines)
        return message
