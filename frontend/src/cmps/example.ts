import { Button, Div, elRef, injectStyles, Span, state as $, type CSSStyles, If } from "../littleLib.js";

const gstate = { value: 1 };

export default function Example(big: boolean = false)
{
	let span = null as HTMLSpanElement | null;
	function change(v: number)
	{
		gstate.value += v;
		if (span) span.innerText = `${gstate.value}`;
	}
	return Div([styles.root, big && styles.root_big], [
		Button(styles.button, "-", () => change(-1)),
		Span({ fontWeight: "bold" }, `${gstate.value}`, el => span = el),
		Button(styles.button, "+", () => change(1)),
	])
}

export function Example2(big: boolean = false)
{
	const value = $(1);
	const span = elRef<HTMLSpanElement>();
	const btnMinusStyle = $<CSSStyles>({ opacity: 1 });
	const btnPlusOpacity = $(1);
	function change(v: number)
	{
		value.v += v;
		span.el.innerText = `${value.v}`;
		btnMinusStyle.v = { opacity: value.v > 0 ? 1 : 0.5 }
		btnPlusOpacity.v = value.v < 5 ? 1 : 0.5
	}
	value.on(v => v == 0, () => console.log("some log for testing"))
	return Div([styles.root, big && styles.root_big], [
		Button([styles.button, btnMinusStyle], "-",
			() => change(-1), el => value.w(v => el.disabled = v < 0)),
		If($(value, v => v == 2),
			["t", Span({ color: "red" }, "w"), "o"],
			Span({
				fontWeight: "bold",
				textDecoration: $(value, v => v == 3 ? "underline" : ""),
			}, `${value.v}`, span.set),
		),
		Button(
			[
				styles.button,
				{ opacity: btnPlusOpacity },
				$(value, v => v == 4 && styles.button_red),
			],
			"+", () => change(1)),
	])
}

const styles = injectStyles({
	root: {
		display: "flex",
		alignItems: "center",
		gap: "0.25em",
	},
	root_big: {
		fontSize: "1.2em",
	},
	"root span": {
		minWidth: "1em",
		textAlign: "center",
	},
	button: {
		background: "var(--primary-400)",
		width: "1.2em",
		height: "1.2em",
		borderRadius: "0.25em",
		transition: "box-shadow 150ms"
	},
	button_red: {
		background: "tomato",
	},
	"button:hover": {
		boxShadow: "0 0 1px 1px var(--primary-400)"
	}
});
