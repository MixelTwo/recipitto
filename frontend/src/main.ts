import { _onPageCleanup, trimStart } from "./littleLib.js";
import render_index from "./pages/index.js";
import render_search from "./pages/search.js";
import render_recipe from "./pages/recipe.js";
import render_recipe_edit from "./pages/recipe_edit.js";
import render_profile from "./pages/profile.js";
import render_admin from "./pages/admin.js";

export const GlobalState = {};

type PageConfig<Args extends Record<string, any>> = {
	render: (args: Args) => void;
	path: string;
};
const createPages = <T extends Record<string, PageConfig<any>>>(p: T) => p;

const QNAV = true;
const pages = createPages({
	"index": { render: render_index, path: "/" },
	"search": { render: render_search, path: "/search" },
	"recipe_create": { render: render_recipe_edit, path: "/recipe/new" },
	"recipe": { render: render_recipe, path: "/recipe/<id>" },
	"recipe_edit": { render: render_recipe_edit, path: "/recipe/<id>/edit" },
	"profile": { render: render_profile, path: "/profile" },
	"admin": { render: render_admin, path: "/admin" },
});
type TPages = typeof pages;
type RenderArgs<T extends keyof TPages> = Parameters<TPages[T]["render"]>[0];

window.addEventListener("popstate", (event) =>
{
	if (event.state && event.state.page in pages)
		_toPage(event.state.page, event.state.args, null, false);
	else
		_toPage("index", undefined, null, false);
});
toPageByUrl(!QNAV ? location.pathname : new URLSearchParams(window.location.search).get("p") || "");

export function toPage<T extends keyof TPages>(
	page: T,
	...args: undefined extends RenderArgs<T>
		? [args?: RenderArgs<T>, query?: Record<string, string | number>]
		: [args: RenderArgs<T>, query?: Record<string, string | number>]
)
{
	const [pageArgs, query] = args;
	_toPage(page, pageArgs, query || {}, true);
}
function _toPage<T extends keyof TPages>(
	page: T,
	args: RenderArgs<T>,
	query: Record<string, string | number> | null | undefined,
	pushState: boolean,
)
{
	_onPageCleanup.forEach(fn => fn());
	_onPageCleanup.splice(0, _onPageCleanup.length);
	const entry = pages[page] as TPages[T];
	const render = entry.render as (args: RenderArgs<T>) => void;
	const path = entry.path.replaceAll(/<.+>/g, v => `${(args as any)?.[v.slice(1, -1)]}`);
	let params = new URLSearchParams(window.location.search);
	if (query)
	{
		params = new URLSearchParams()
		for (const key in query)
		{
			if (!Object.hasOwn(query, key)) continue;
			const val = query[key];
			params.set(key, `${val}`);
		}
	}
	if (QNAV) params.set("p", path);
	const fullpath = (!QNAV ? path : location.pathname) + "?" + params.toString();
	if (pushState) window.history.pushState({ page, args }, "", fullpath);
	else window.history.replaceState({ page, args }, "", fullpath);
	render(args);
}

function toPageByUrl(pathname: string)
{
	for (const key in pages)
	{
		if (!Object.hasOwn(pages, key)) continue;
		console.log(key);
		const { path } = pages[key as keyof TPages];
		if (pathname == path)
		{
			_toPage(key as keyof TPages, {}, null, false);
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
			_toPage(key as keyof TPages, args as any, null, false);
			return;
		}
	}
	_toPage("index", undefined, null, false);
}
