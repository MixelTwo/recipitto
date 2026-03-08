import Example from "../cmps/example.js";
import Layout from "../layout.js";
import { H1 } from "../littleLib.js";
import { setPageTitle } from "../utils.js";

export default function render({ id }: { id: string })
{
	setPageTitle(`Item ${id}`);
	Layout([
		H1([], `Item ${id}`),
		Example(true),
	]);
}