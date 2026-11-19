# Runs containers.podman.podman_container with the options it is given, as a
# dict.
#
# A task cannot hand a whole dict to a module without templating its `args`,
# which ansible-core flags on every run while facts are injected as variables:
# https://docs.ansible.com/ansible/latest/reference_appendices/faq.html#argsplat-unsafe
# An action plugin can : it passes the dict on as data, and the module's own
# argument spec rejects an option it does not know.

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):

    _supports_check_mode = True

    def run(self, tmp=None, task_vars=None):
        result = super().run(tmp, task_vars)

        _, args = self.validate_argument_spec(
            argument_spec={
                'options': {'type': 'dict', 'required': True},
                'preview_replacement': {'type': 'bool', 'default': False},
            },
        )
        options = args['options']
        if args['preview_replacement']:
            if not self._task.check_mode:
                raise AnsibleActionFail('preview_replacement requires check mode')
            options = options.copy()
            # Unit generation writes to its configured path even in check mode.
            # Keep the implicit rm from generate_systemd.new for the comparison.
            if options.pop('generate_systemd', {}).get('new'):
                options.pop('remove', None)
                options.pop('auto_remove', None)
                options['rm'] = True
            options.pop('restart', None)
            options['force_restart'] = False

        result.update(self._execute_module(
            module_name='containers.podman.podman_container',
            module_args=options,
            task_vars=task_vars,
        ))
        return result
