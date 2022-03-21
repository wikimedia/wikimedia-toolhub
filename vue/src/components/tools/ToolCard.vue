<template>
	<v-card
		class="tool-card__card pa-0"
		height="280px"
		:to="{ name: 'tools-view', params: { name: tool.name } }"
		outlined
	>
		<v-toolbar
			dense
			color="accent base"
			class="ps-4 ma-0"
			elevation="0"
		>
			<v-spacer />
			<ToolMenu :tool="tool"
				:smallicon="true"
				@click.stop
			/>
		</v-toolbar>
		<v-card-title class="flex-nowrap">
			<ToolImage
				class="me-2"
				:tool="tool"
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
				<dd class="line-clamp span-comma-list">
					<span
						v-for="author in tool.author"
						:key="author.name"
					>{{ author.name }}</span>
				</dd>
			</dl>
		</v-card-text>
	</v-card>
</template>

<script>
import ToolImage from '@/components/tools/ToolImage';
import ToolMenu from '@/components/tools/ToolMenu';

export default {
	name: 'ToolCard',
	components: {
		ToolImage,
		ToolMenu
	},
	props: {
		tool: {
			type: Object,
			required: true
		}
	}
};
</script>
