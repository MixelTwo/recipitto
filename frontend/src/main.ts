import render_index from "./pages/index.js";
import render_item from "./pages/item.js";

export const GlobalState = {

};

type PageConfig<Args extends Record<string, any>> = {
	render: (args: Args) => void;
	path: string;
};
const createPages = <T extends Record<string, PageConfig<any>>>(p: T) => p;

const pages = createPages({
	"index": { render: render_index, path: "/" },
	"item": { render: render_item, path: "/item/<id>" },
});
type TPages = typeof pages;
type RenderArgs<T extends keyof TPages> = Parameters<TPages[T]["render"]>[0];

window.addEventListener("popstate", (event) =>
{
	if (event.state && event.state.page in pages)
		_toPage(event.state.page, event.state.args, false);
	else
		_toPage("index", undefined, false);
});
toPageByUrl(location.pathname);

export function toPage<T extends keyof TPages>(
	page: T,
	...args: keyof RenderArgs<T> extends never
		? [args?: RenderArgs<T>]
		: [args: RenderArgs<T>]
)
{
	_toPage(page, args[0], false);
}
function _toPage<T extends keyof TPages>(
	page: T,
	args: RenderArgs<T>,
	pushState: boolean,
)
{
	const entry = pages[page] as TPages[T];
	const render = entry.render as (args: RenderArgs<T>) => void;
	const path = entry.path.replaceAll(/<.+>/g, v => `${(args as any)?.[v.slice(1, -1)]}`);
	if (pushState) window.history.pushState({ page, args }, "", path);
	else window.history.replaceState({ page, args }, "", path);
	render(args);
}

function toPageByUrl(pathname: string)
{
	for (const key in pages)
	{
		if (!Object.hasOwn(pages, key)) continue;
		const { path } = pages[key as keyof TPages];
		if (pathname == path)
		{
			_toPage(key as keyof TPages, undefined, false);
			return;
		}
		if (!path) continue;
		const argNames = [] as string[];
		const m = RegExp("^" + path.replaceAll(/<.+>/g, v =>
		{
			argNames.push(v.slice(1, -1));
			return `([^\\/]+)`;
		}) + "$").exec(pathname);
		if (m)
		{
			const args: Record<string, string> = {};
			argNames.forEach((name, i) => args[name] = m[i + 1] || "");
			_toPage(key as keyof TPages, args as any, false);
			return;
		}
	}
	_toPage("index", undefined, false);
}
