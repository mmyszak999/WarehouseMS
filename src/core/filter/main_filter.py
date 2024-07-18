import operator

from sqlalchemy.sql.expression import Select

from src.core.exceptions import UnavailableFilterFieldException, NoSuchFieldException


class Filter(Select):
    def __init__(self, model, inst, current_model=None):
        self.main_model = model
        self.inst = inst
        self.current_model = current_model
        self.field = None
        self.filter_params = None

    def __lt__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) < other)

    def __gt__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) > other)

    def __ge__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) >= other)

    def __le__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) <= other)

    def __eq__(self, other):
        values = other.split(",")
        if len(values) > 1:
            return self.inst.filter(getattr(self.current_model, self.field).in_(values))
        return self.inst.filter(getattr(self.current_model, self.field) == other)

    def __ne__(self, other):
        return self.inst.filter(getattr(self.current_model, self.field) != other)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def set_filter_params(self, query_params: list[tuple]) -> None:
        from src.core.utils.filter import filter_query_param_values_extractor

        self.filter_params = filter_query_param_values_extractor(query_params)

    def perform_filter(self, field, operation, value):
        from src.core.utils.filter import get_model_from_key_name, FORBIDDEN_FIELDS

        if len(field.split("__")) == 1:
            self.field = field
            self.current_model = self.main_model
        else:
            key, self.field = field.split("__")
            self.current_model = get_model_from_key_name(self.main_model, key)
        if self.field in FORBIDDEN_FIELDS:
            raise UnavailableFilterFieldException(field=self.field)
        
        try:
            inst = getattr(operator, operation)(self, value)
            result = Filter(self.main_model, inst, self.current_model)
            return result
        except AttributeError:
            raise NoSuchFieldException(
                model_name=self.current_model.__name__,
                field=self.field
            )

    def get_filtered_instances(self):
        for param in self.filter_params:
            self.inst = self.perform_filter(*param).inst
        return self.inst