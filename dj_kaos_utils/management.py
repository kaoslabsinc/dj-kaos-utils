from django.core.management import BaseCommand


class TaskCommand(BaseCommand):
    """
    An abstraction over :class:`django.core.management.BaseCommand` to run tasks from the django manage.py cli services
    """

    def _print_success(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def run_task(self, *args, **options):
        """
        Override this method to run your task. You have access to `options` and `args`

        :return: A meaningful summary of the task run. E.g. number of rows updated.
        """
        raise NotImplementedError

    def print_success_message(self, return_val):
        """
        Override this method to change the success message being printed. You have access

        :param return_val: return value from :func:`run_task`
        """
        self._print_success("Done!")

    def handle(self, *args, **options):
        return_val = self.run_task(*args, **options)
        self.print_success_message(return_val)
