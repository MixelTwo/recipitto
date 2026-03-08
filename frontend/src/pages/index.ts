import Example, { Example2 } from "../cmps/example.js";
import Layout from "../layout.js";
import { A, Div } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";

export default function render()
{
	setPageTitle("");
	Layout([
		Div("index__list", [
			A([], "to item 1", "/item/1", () => toPage("item", { id: "1" })),
			A([], "to item 2", "/item/2", () => toPage("item", { id: "2" })),
			Example2(),
		]),
	]);
}