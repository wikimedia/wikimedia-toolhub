<template>
	<v-card
		class="tool-card__card pa-1"
		height="220px"
		:to="`/tool/${tool.name}`"
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
			<dl class="tool-card__authors row mx-0 my-4 text-subtitle-1">
				<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
				<dd class="line-clamp">{{ tool.author }}</dd>
			</dl>
		</v-card-text>
	</v-card>
</template>

<script>
import CommonsImage from '@/components/common/CommonsImage';

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
