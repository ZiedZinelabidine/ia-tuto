<script lang="ts">
import Fuse from 'fuse.js'; import Bolt from '$lib/components/icons/Bolt.svelte'; import { onMount, getContext } from 'svelte'; import { settings, WEBUI_NAME } from '$lib/stores'; import { WEBUI_VERSION } from '$lib/constants'; const i18n = getContext('i18n');

	export let suggestionPrompts = [];
	export let className = '';
	export let inputValue = '';
	export let onSelect = (e) => {};

	$: customPrompts = [
		{
			id: 'chiffrage',
			title: [$i18n.t('How to contact Zied?'), $i18n.t('Contact Zied for a new project')],
			content: $i18n.t('Contactez Zied Zinelabidine pour un nouveau projet')
		},
		{
			id: 'cout-tache',
			title: [$i18n.t('Who is Zied?'), $i18n.t('Zied’s presentation')],
			content: $i18n.t(
				'Presentation de Zied.'
			)
		},
		{
			id: 'solution',
			title: [$i18n.t('What are Zied’s availabilities for an online meeting?'), $i18n.t('Check Zied’s availability for an online meeting')],
			content: $i18n.t(
				'Quelles sont les disponibilités de Zied pour un rendez-vous en ligne ?'
			)
		}
	];

	$: sortedPrompts = customPrompts;
	let filteredPrompts = customPrompts;

	const fuseOptions = {
		keys: ['content', 'title'],
		threshold: 0.5
	};

	let fuse;

	$: fuse = new Fuse(sortedPrompts, fuseOptions);

	const getFilteredPrompts = (value: string) => {
		if (value.length > 500) {
			filteredPrompts = [];
			return;
		}

		filteredPrompts =
			value.trim() && fuse
				? fuse.search(value.trim()).map((result) => result.item)
				: sortedPrompts;
	};

	$: getFilteredPrompts(inputValue);
</script>

<div class="mb-1 flex gap-1 text-xs font-medium items-center text-gray-600 dark:text-gray-400">
	{#if filteredPrompts.length > 0}
		<Bolt />
		{$i18n.t('Suggested')}
	{:else}
		<!-- Keine Vorschläge -->

		<div
			class="flex w-full {$settings?.landingPageMode === 'chat'
				? ' -mt-1'
				: 'text-center items-center justify-center'}  self-start text-gray-600 dark:text-gray-400"
		>
			{$WEBUI_NAME} ‧ v{WEBUI_VERSION}
		</div>
	{/if}
</div>

<div class="h-40 w-full">
	{#if filteredPrompts.length > 0}
		<div role="list" class="max-h-40 overflow-auto scrollbar-none items-start {className}">
			{#each filteredPrompts as prompt, idx (prompt.id || `${prompt.content}-${idx}`)}
				<!-- svelte-ignore a11y-no-interactive-element-to-noninteractive-role -->
				<button
					role="listitem"
					class="waterfall flex flex-col flex-1 shrink-0 w-full justify-between
				       px-3 py-2 rounded-xl bg-transparent hover:bg-black/5
				       dark:hover:bg-white/5 transition group"
					style="animation-delay: {idx * 60}ms"
					on:click={() => onSelect({ type: 'prompt', data: prompt.content })}
				>
					<div class="flex flex-col text-left">
						{#if prompt.title && prompt.title[0] !== ''}
							<div
								class="font-medium dark:text-gray-300 dark:group-hover:text-gray-200 transition line-clamp-1"
							>
								{prompt.title[0]}
							</div>
							<div class="text-xs text-gray-600 dark:text-gray-400 font-normal line-clamp-1">
								{prompt.title[1]}
							</div>
						{:else}
							<div
								class="font-medium dark:text-gray-300 dark:group-hover:text-gray-200 transition line-clamp-1"
							>
								{prompt.content}
							</div>
							<div class="text-xs text-gray-600 dark:text-gray-400 font-normal line-clamp-1">
								{$i18n.t('Prompt')}
							</div>
						{/if}
					</div>
				</button>
			{/each}
		</div>
	{/if}
</div>

<style>
	/* Waterfall animation for the suggestions */
	@keyframes fadeInUp {
		0% {
			opacity: 0;
			transform: translateY(20px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.waterfall {
		opacity: 0;
		animation-name: fadeInUp;
		animation-duration: 200ms;
		animation-fill-mode: forwards;
		animation-timing-function: ease;
	}
</style>
