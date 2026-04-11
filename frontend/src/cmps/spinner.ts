import { Div, Span } from "../littleLib.js";

/**
 * Loading spinner component.
 *
 * @returns A div element with spinner styling
 */
export default function Spinner()
{
	return Div("spinner", Span());
}