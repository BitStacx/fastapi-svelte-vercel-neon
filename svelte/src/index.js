import { mount } from "svelte";
import Index from "./pages/Index.svelte";
import "./app.css";

document.addEventListener("DOMContentLoaded", () => {
	const target = document.getElementById("app");
	const propsElement = document.getElementById("app-props");
	const props = propsElement ? JSON.parse(propsElement.textContent) : {};

	if (target) {
		mount(Index, {
			target: target,
			props: props,
		});
	} else {
		console.error(
			"Index mount target not found. Ensure the template tag is configured correctly."
		);
	}
});
