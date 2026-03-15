import { wait } from "./littleLib.js";

export function setPageTitle(title: string, prefix: string = "Recipitto")
{
	if (prefix && title) title = prefix + " | " + title;
	else if (prefix && !title) title = prefix;
	document.title = title;
}

export async function mockFetch<T>(url: RequestInfo | URL, res: T, body?: any)
{
	console.log(`fetch ${url}`);
	await wait(250);
	return res;
}
