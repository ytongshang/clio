from .singleton import AbstractSingleton


class PerformanceItem:
    module_name: str
    function_name: str
    count: int = 0
    min: float = 0.0
    max: float = 0.0
    average: float = 0.0

    def to_json(self):
        return {
            "module_name": self.module_name,
            "function_name": self.function_name,
            "count": self.count,
            "min": self.min,
            "max": self.max,
            "average": self.average,
        }


def _performance_sort_by(item: dict):
    return item["average"]


class Performance(AbstractSingleton):
    record: dict[str, PerformanceItem] = {}

    def add(self, module_name: str, function_name: str, time: float):
        key = module_name + function_name
        item = self.record.get(key)
        if item is None:
            item = PerformanceItem()
            item.module_name = module_name
            item.function_name = function_name
            self.record[key] = item
        if item.min == 0:
            item.min = time
        else:
            item.min = min(item.min, time)
        item.max = max(item.min, time)
        item.average = ((item.average * item.count) + time) / (item.count + 1)
        item.count = item.count + 1

    def all(self):
        result = []
        for key, value in self.record.items():
            result.append(value.to_json())
        sorted(result, key=_performance_sort_by, reverse=True)
        return result

    def get_by_name(self, name: str):
        result = []
        for key, value in self.record.items():
            if value.function_name == name:
                result.append(value.to_json())
        sorted(result, key=_performance_sort_by, reverse=True)
        return result
