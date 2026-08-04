# Writing an agent adapter

DeskCert never calls a model API directly. An `AgentAdapter` is the one interface you
implement to wire up a real agent: given the current page state, return the next action.

## TypeScript

```ts
// my-agent-adapter.ts
import type { AgentAdapter, AgentAction, AgentObservation } from "deskcert-cli";

export default class MyAgentAdapter implements AgentAdapter {
  name = "my-agent";

  async nextAction(observation: AgentObservation): Promise<AgentAction> {
    // observation.screenshotBase64 -- current page screenshot, PNG, base64
    // observation.axTree           -- simplified page text dump
    // observation.goal             -- the task's natural-language goal
    // observation.allowedActions / observation.forbiddenActions

    const response = await callYourAgent({
      goal: observation.goal,
      screenshot: observation.screenshotBase64,
      pageText: observation.axTree,
    });

    return {
      type: response.actionType,   // "click" | "fill" | "navigate" | "read" | "finish"
      name: response.actionName,   // matched against forbidden_actions -- name it precisely
      selector: response.selector,
      value: response.value,
    };
  }
}
```

```
deskcert run --agent my-agent --adapter-module ./my-agent-adapter.js --suite ./deskcert-suite
```

Build the adapter file first (`npm run build` or your own bundler) -- `--adapter-module` loads
a compiled JS module, not a `.ts` file directly.

## Python

```python
# my_agent_adapter.py
from deskcert import AgentAction, AgentAdapter, AgentObservation

class Adapter(AgentAdapter):
    name = "my-agent"

    async def next_action(self, observation: AgentObservation) -> AgentAction:
        response = await call_your_agent(
            goal=observation.goal,
            screenshot=observation.screenshot_base64,
            page_text=observation.ax_tree,
        )
        return AgentAction(
            type=response.action_type,
            name=response.action_name,
            selector=response.selector,
            value=response.value,
        )
```

```
deskcert run --agent my-agent --adapter-module ./my_agent_adapter.py --suite ./deskcert-suite
```

## Naming forbidden actions precisely

`forbidden_actions` in a task definition matches against the `name` you set on a returned
action (falling back to `type` if `name` is omitted). Name the operations that actually
matter -- `delete_record`, `submit_payment`, `send_email` -- rather than relying on the
generic action `type` (`click`, `fill`) alone, since almost every real action is a `click` or
a `fill` under the hood.

## Security note

`--adapter-module` executes a local file as code -- the same trust model as an ESLint plugin
or a pytest plugin. Only point it at adapter modules you wrote or reviewed yourself. DeskCert
never downloads or executes an adapter module from a URL or a registry on your behalf.
