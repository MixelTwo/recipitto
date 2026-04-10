export function getButton(id: string)
{
	return getEl(id, HTMLButtonElement);
}
export function getDiv(id: string)
{
	return getEl(id, HTMLDivElement);
}
export function getCanvas(id: string)
{
	return getEl(id, HTMLCanvasElement);
}
export function getInput(id: string)
{
	return getEl(id, HTMLInputElement);
}
export function getEl<T extends typeof HTMLElement>(id: string, type: T)
{
	const el = <unknown | null>document.getElementById(id);
	if (el == null) throw new Error(`${id} not found`);
	if (el instanceof type) return el as InstanceType<T>;
	throw new Error(`${id} element not ${type.name}`);
}


export function randomInt(max: number): number;
export function randomInt(min: number, max: number): number;
export function randomInt(maxmin: number, max?: number)
{
	if (max != undefined)
		return Math.floor(Math.random() * (maxmin - max)) + max;
	return Math.floor(Math.random() * maxmin);
}
export function chooseRandom<T>(array: T[])
{
	return array[randomInt(0, array.length)];
}
export function shuffle<T>(array: T[])
{
	return array.sort(() => 0.5 - Math.random());
}
export function randomColor()
{
	return hslColor(randomInt(0, 360), randomInt(80, 100), randomInt(40, 80));
}
export function randomStr(len: number): string
{
	const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	let result = "";
	for (let i = 0; i < len; i++)
		result += chars.charAt(randomInt(chars.length));
	return result;
}



export function addButtonListener(id: string, f: (e: MouseEvent, btn: HTMLButtonElement) => void)
{
	const button = getButton(id);
	button.addEventListener("click", e => f(e, button));
	return button;
}
export function addLinkListener(id: string, f: (e: MouseEvent, a: HTMLAnchorElement) => void)
{
	const a = getEl(id, HTMLAnchorElement);
	a.addEventListener("click", e =>
	{
		e.preventDefault();
		f(e, a);
	});
}
export function capitalize(text: string)
{
	return text.slice(0, 1).toUpperCase() + text.slice(1);
}
export const toCapitalCase = capitalize;
export function copyText(text: string)
{
	const el = document.createElement('textarea');
	el.value = text;
	el.setAttribute('readonly', '');
	el.style.position = 'absolute';
	el.style.left = '-9999px';
	el.style.opacity = '0';
	document.body.appendChild(el);
	el.select();
	document.execCommand('copy');
	document.body.removeChild(el);
}
export function downloadFile(filename: string, text: string)
{
	var el = document.createElement('a');
	el.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
	el.setAttribute('download', filename);

	el.style.display = 'none';
	document.body.appendChild(el);

	el.click();

	document.body.removeChild(el);
}

export async function wait(t: number)
{
	return new Promise(res => setTimeout(res, t));
}
/**
 *
 * @param h in range [0; 360]
 * @param s in range [0; 100]
 * @param l in range [0; 100]
 * @returns `hsl(${h}, ${s}%, ${l}%)`
 */
export function hslColor(h: number, s: number, l: number)
{
	return `hsl(${h}, ${s}%, ${l}%)`;
}
/**
 *
 * @param r in range [0; 255]
 * @param g in range [0; 255]
 * @param b in range [0; 255]
 * @returns `hsl(${h}, ${s}%, ${l}%)`
 */
export function rgbColor(r: number, g: number, b: number)
{
	return `hsl(${r}, ${g}%, ${b}%)`;
}
export function lerp(v1: number, v2: number, t: number)
{
	return (v2 - v1) * t + v1;
}
export function clamp(v: number, min: number, max: number)
{
	return Math.min(Math.max(v, min), max);
}
export function dateNow(split = ".")
{
	const date = new Date();
	return [date.getFullYear(), date.getMonth() + 1, date.getDate()].join(split);
}
export function numNoun(num: number, one: string, two: string, five: string)
{
	num = Math.abs(num);
	num %= 100;
	if (num >= 5 && num <= 20) return five;
	num %= 10;
	if (num == 1) return one;
	if (num >= 2 && num <= 4) return two;
	return five;
}
export function trimEnd(str: string, ...chs: string[]): string
{
	if (!chs.length) return str.trimEnd();
	const pattern = new RegExp(`(?:${chs.map(escapeRegExp).join("|")})+$`);
	return str.replace(pattern, "");
}

export function trimStart(str: string, ...chs: string[]): string
{
	if (!chs.length) return str.trimStart();
	const pattern = new RegExp(`^(?:${chs.map(escapeRegExp).join("|")})+`);
	return str.replace(pattern, "");
}
export function escapeRegExp(string: string)
{
	return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}


export function SetContent(parent: HTMLElement, children: ElChildren)
{
	parent.innerHTML = "";
	AppendContent(parent, children);
}
export function AppendContent(parent: HTMLElement, children: ElChildren)
{
	if (children instanceof Array)
		children.forEach(ch => AppendContent(parent, ch));
	else if (children instanceof State)
		If(children, () => children.v).forEach(ch => AppendContent(parent, ch));
	else if (children)
		parent.append(children);
}

export function Div(classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLDivElement) => void)
{
	return initEl("div", classes, children, onCreate);
}
export function Span(classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLSpanElement) => void)
{
	return initEl("span", classes, children, onCreate);
}
export function H1(classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLHeadingElement) => void)
{
	return initEl("h1", classes, children, onCreate);
}
export function Table(classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLTableElement) => void)
{
	return initEl("table", classes, children, onCreate);
}
export function TR(classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLTableRowElement) => void)
{
	return initEl("tr", classes, children, onCreate);
}
export function TD(classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLTableCellElement) => void)
{
	return initEl("td", classes, children, onCreate);
}
export function Input(classes?: ElClasses, type?: string, placeholder?: string, onCreate?: (el: HTMLInputElement) => void)
{
	const input = initEl("input", classes, undefined);
	if (type) input.type = type;
	if (placeholder) input.placeholder = placeholder;
	onCreate?.(input);
	return input;
}
export function Button(classes?: ElClasses, children?: ElChildren, clickListener?: (btn: HTMLButtonElement) => void, onCreate?: (el: HTMLButtonElement) => void)
{
	const button = initEl("button", classes, children, onCreate);
	if (clickListener) button.addEventListener("click", clickListener.bind(button, button));
	return button;
}
export function A(classes?: ElClasses, children?: ElChildren, href?: string, clickListener?: (a: HTMLAnchorElement) => void, onCreate?: (el: HTMLAnchorElement) => void)
{
	const a = initEl("a", classes, children, onCreate);
	if (href)
	{
		a.href = href || "";
		a.target = "_blank";
	}
	if (clickListener) a.addEventListener("click", e =>
	{
		e.preventDefault();
		clickListener.bind(a, a)();
	});
	return a;
}

export type CSSStyles = Partial<Record<keyof CSSStyleDeclaration, string | number>>;
export type CSSStylesState = Partial<Record<keyof CSSStyleDeclaration, string | number | State<string | number>>>;
type ElClassSimple = string | undefined | null | false | CSSStyles;
type ElClass = ElClassSimple | CSSStylesState | State<ElClass>;
export type ElClasses = ElClass[] | ElClass;
type ElChild = Node | string | undefined | null | false | ElChild[];
export type ElChildren = ElChild | State<ElChildren> | (ElChild | State<ElChildren>)[];
export function initEl<K extends keyof HTMLElementTagNameMap>(tagName: K, classes?: ElClasses, children?: ElChildren, onCreate?: (el: HTMLElementTagNameMap[K]) => void)
{
	const el = document.createElement(tagName);
	if (classes)
	{
		function addClass(c: ElClass)
		{
			if (!c) return;
			if (typeof c == "string") c.split(" ").forEach(cls => el.classList.add(cls));
			else if (c instanceof State)
			{
				function update(v: ElClass, pv: ElClass)
				{
					if (pv)
					{
						if (typeof pv == "string") el.classList.remove(pv);
						else Object.keys(pv).forEach(k => el.style[k as any] = "");
					}
					addClass(v);
				}
				c.addListener(update)
				update(c.v, undefined);
			}
			else Object.keys(c).forEach(k =>
			{
				const key = k as Exclude<keyof CSSStyleDeclaration, "length" | "parentRule">;
				const v = (c as CSSStylesState)[key]!;
				if (v instanceof State)
				{
					function update(v: string | number)
					{
						el.style[key] = styleValuetoString(k, v!) as any;
					}
					v.addListener(update)
					update(v.v);
				}
				else
				{
					el.style[key] = styleValuetoString(k, v!) as any;
				}
			})
		}
		if (typeof classes == "string") classes.split(" ").forEach(cls => el.classList.add(cls));
		if (classes instanceof Array) classes.forEach(addClass);
		else addClass(classes);
	}
	if (children)
	{
		function appendChildren(children: ElChildren)
		{
			if (children instanceof Array)
				children.forEach(appendChildren);
			else if (children instanceof State)
				If(children, () => children.v).forEach(appendChildren);
			else if (children)
				el.append(children);
		}
		appendChildren(children);
	}
	onCreate?.(el);

	return el;
}

export function createSvgEl<K extends keyof SVGElementTagNameMap>(qualifiedName: K, parent?: Node): SVGElementTagNameMap[K]
{
	const el = document.createElementNS("http://www.w3.org/2000/svg", qualifiedName);
	if (parent)
		parent.appendChild(el);
	return el;
}

const UNITLESS_PROPS = new Set([
	"opacity", "zIndex", "fontWeight", "lineHeight",
	"flex", "flexGrow", "flexShrink", "order", "zoom", "columnCount"
]);

function styleValuetoString(key: string, val: string | number)
{
	return (typeof val === "number" && !UNITLESS_PROPS.has(key))
		? `${val}px`
		: `${val}`;

}

export function injectStyles<T extends Record<string, CSSStyles | Record<string, CSSStyles>>>(styles: T): Record<keyof T, string>
{
	const styleElement = document.createElement("style");
	const classMap = {} as Record<keyof T, string>;
	let cssString = "";

	const toKebab = (str: string) => str.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase();
	const generateHash = () => Math.random().toString(36).slice(2, 9);

	function buildCSS(className: string, values: CSSStyles | Record<string, CSSStyles>)
	{
		const rules = [] as string[];
		for (const prop in values)
		{
			if (!Object.prototype.hasOwnProperty.call(values, prop)) continue;
			const value = values[prop as keyof typeof values];
			if (typeof value == "object")
			{
				buildCSS(
					prop.includes("&") ? prop.replaceAll("&", className) : className + " " + prop
					, value
				);
			}
			else if (value != undefined)
			{
				rules.push(`  ${toKebab(prop)}: ${styleValuetoString(prop, value)};`);
			}
		}
		cssString += `${className} {\n${rules.join("\n")}\n}\n`;
	}

	const styleItems = Object.entries(styles)
	for (const [key, values] of styleItems)
	{
		if (!Object.prototype.hasOwnProperty.call(styles, key)) continue;
		const match = key.match(/^([^:\s]+)(.*)$/);
		const base = match?.[1] ?? key;
		const suffix = match?.[2] ?? "";

		const baseClass = classMap[base] ?? `${base}_${generateHash()}`;
		const className = baseClass + suffix
		classMap[key as keyof T] = className;

		buildCSS("." + className, values);
	}

	styleElement.textContent = cssString;
	document.head.appendChild(styleElement);

	return classMap;
}

type StateListener<T> = (v: T, pv: T) => void;
let _onPageCleanup: (() => void)[] = [];
export function onPageCleanup(fn: () => void)
{
	_onPageCleanup.push(fn);
}
export function runPageCleanup()
{
	_onPageCleanup.forEach(fn => fn());
	_onPageCleanup = [];
}
export class State<T>
{
	private value: T;
	private listeners: StateListener<any>[] = [];
	public get v() { return this.value; }
	public set v(value: T)
	{
		const pv = this.value;
		this.value = value;
		this.notifyChange(value, pv);
	}
	constructor(value: T)
	{
		this.value = value;
		onPageCleanup(() => this.listeners = []);
	}
	public notifyChange(value: T, pv: T)
	{
		this.listeners.forEach(f => f(value, pv));
	}

	public addListener(listener: StateListener<T>)
	{
		this.listeners.push(listener);
	}
	public w = this.addListener;
	public removeListener(listener: StateListener<T>)
	{
		const i = this.listeners.indexOf(listener);
		if (i >= 0) this.listeners.splice(i, 1);
	}
	public on(cond: (v: T) => boolean, fn: () => any)
	{
		this.addListener(v => cond(v) && fn());
	}
}
export const $ = state;
export function state<T>(v: T): State<T>
export function state<T, K>(v: State<T>, transformer: (v: T) => K): State<K>
export function state<T, K>(v: State<T> | T, transformer?: (v: T) => K): State<K>
{
	const tfn = transformer || ((v: any) => v);
	if (v instanceof State)
	{
		const s = new State(tfn(v.v));
		v.addListener(nv => s.v = tfn(nv));
		return s;
	}
	return new State(tfn(v));
}
export function elRef<T extends HTMLElement>()
{
	const ref = {
		el: null as any as T,
		set(el: T) { ref.el = el; },
	}
	return ref;
}
export function If<T>(state: State<T>, t: ElChildren | (() => ElChildren), f?: ElChildren | (() => ElChildren)): Node[]
{
	let _nodesT: Node[];
	const getNodesT = () =>
	{
		if (typeof t == "function") return childrenToNodes(t());
		if (!_nodesT) _nodesT = childrenToNodes(t);
		return _nodesT;
	};
	let _nodesF: Node[];
	const getNodesF = () =>
	{
		if (typeof f == "function") return childrenToNodes(f());
		if (!_nodesF) _nodesF = childrenToNodes(f);
		return _nodesF;
	};
	let els = state.v ? getNodesT() : getNodesF();
	state.addListener((v, pv) =>
	{
		if (v == pv) return;
		const newEls = v ? getNodesT() : getNodesF();
		const pastNode = els[0];
		const parent = pastNode?.parentNode;
		if (!parent) return;
		newEls.forEach(el => parent.insertBefore(el, pastNode));
		els.forEach(el => parent.removeChild(el));
		els = newEls;
	});
	function childrenToNodes(children: ElChildren): Node[]
	{
		const nodes = [] as Node[];
		function append(children: ElChildren)
		{
			if (children instanceof Array)
				children.forEach(append);
			else if (typeof children == "string")
				nodes.push(document.createTextNode(children));
			else if (children instanceof State)
				If(children, () => children.v).forEach(n => nodes.push(n));
			else if (children)
				nodes.push(children);
		}
		append(children);
		if (nodes.length == 0)
			nodes.push(document.createComment("placeholder"));
		return nodes;
	}
	return els;
}

export class FetchError extends Error
{
	constructor(message: string, public status: number)
	{
		super(message)
	}
}
async function fetchWithJson(method: "GET" | "POST" | "DELETE" | "PATCH", url: RequestInfo | URL, body?: any)
{
	const res = await fetch(url, {
		method,
		headers: body === undefined ? {} : {
			"Content-Type": "application/json"
		},
		body: body === undefined ? null : JSON.stringify(body),
	});
	if (!res.ok)
	{
		let msg = "";
		try { msg = (await res.json() as { msg: string }).msg; } catch { }
		throw new FetchError(msg, res.status)
	}
	return res;
}

export function fetchGet(url: RequestInfo | URL)
{
	return fetchWithJson("GET", url);
}

export function fetchPost(url: RequestInfo | URL, body?: any)
{
	return fetchWithJson("POST", url, body);
}

export function fetchDelete(url: RequestInfo | URL, body?: any)
{
	return fetchWithJson("DELETE", url, body);
}

export function fetchPatch(url: RequestInfo | URL, body?: any)
{
	return fetchWithJson("PATCH", url, body);
}

async function fetchJson<T>(method: "GET" | "POST" | "DELETE" | "PATCH", url: RequestInfo | URL, body?: any)
{
	const res = await fetchWithJson(method, url, body);
	const data = await res.json();
	return data as T;
}

export function fetchJsonGet<T>(url: RequestInfo | URL)
{
	return fetchJson<T>("GET", url);
}

export function fetchJsonPost<T>(url: RequestInfo | URL, body?: any)
{
	return fetchJson<T>("POST", url, body);
}

export function fetchJsonDelete<T>(url: RequestInfo | URL, body?: any)
{
	return fetchJson<T>("DELETE", url, body);
}

export function fetchJsonPatch<T>(url: RequestInfo | URL, body?: any)
{
	return fetchJson<T>("PATCH", url, body);
}
