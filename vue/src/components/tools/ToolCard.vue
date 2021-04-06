<template>
	<v-card
		class="tool-card__card"
		height="550px"
	>
		<v-card-title class="flex-nowrap">
			<CommonsImage
				class="me-2"
				:commons-url="tool.icon"
				:size="50"
			/>
			<div class="tool-card__title line-clamp">
				{{ tool.title }}
			</div>
		</v-card-title>
		<v-card-text class="py-0">
			<div class="tool-card__desc text--primary line-clamp" dir="auto">
				{{ tool.description }}
			</div>
			<dl class="row mx-0 my-4 text-subtitle-1">
				<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
				<dd>{{ tool.author }}</dd>
			</dl>
			<v-divider />
		</v-card-text>
		<v-card-text class="py-0">
			<v-chip-group
				v-if="tool.keywords"
				active-class="primary--text"
				column
			>
				<v-chip
					v-for="tt in tool.keywords.filter(e => e).slice(0, 5)"
					:key="tt"
				>
					{{ tt }}
				</v-chip>
			</v-chip-group>
		</v-card-text>
		<v-card-actions class="ma-2">
			<v-btn
				color="primary"
				dark
				block
				:to="`/tool/${tool.name}`"
			>
				<v-icon
					dark
					class="pe-1"
				>
					mdi-information-outline
				</v-icon>
				{{ $t( 'learnmore' ) }}
			</v-btn>
			<v-spacer />
			<v-btn
				color="primary"
				dark
				block
				:href="`${tool.url}`"
				target="_blank"
			>
				<v-icon
					dark
					class="pe-1"
				>
					mdi-link-variant
				</v-icon>
				{{ $t( 'browsetool' ) }}
			</v-btn>
		</v-card-actions>
	</v-card>
</template>

<script>
import CommonsImage from '@/components/tools/CommonsImage';

export default {
	name: 'ToolCard',
	components: {
		CommonsImage
	},
	props: {
		tool: {
			type: Object,
			required: true
		}
	}
};
</script>
