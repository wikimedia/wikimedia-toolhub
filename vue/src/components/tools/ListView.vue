<template>
	<v-card
		class="mx-auto"
		outlined
		elevation="1"
	>
		<v-row class="box-header" no-gutters>
			<CommonsImage
				class="my-2 mx-2"
				:commons-url="list.icon"
				:size="40"
			/>
			<v-col>
				<h2 class="text-h6 my-4">
					{{ list.title }}
				</h2>
			</v-col>
			<v-col v-if="list.description" cols="auto">
				<v-btn
					class="transparent elevation-0 my-3"
					@click="listInfo = !listInfo"
				>
					<v-icon size="30" color="secondary">
						mdi-information-outline
					</v-icon>
				</v-btn>
			</v-col>
		</v-row>
		<v-alert
			class="ma-2"
			:value="listInfo"
			color="base90"
			dismissible
			@input="closeListInfo"
		>
			{{ list.description }}
		</v-alert>
		<v-sheet
			class="mx-auto"
			min-width="300"
		>
			<v-slide-group
				show-arrows
			>
				<v-slide-item
					v-for="( tool, idx ) in list.tools"
					:key="`tool.title-${idx}`"
				>
					<v-card
						class="ma-4"
						width="220"
					>
						<ToolCard :tool="tool" />
					</v-card>
				</v-slide-item>
			</v-slide-group>
		</v-sheet>
	</v-card>
</template>

<script>
import ToolCard from '@/components/tools/ToolCard';
import CommonsImage from '@/components/tools/CommonsImage';

export default {
	components: {
		ToolCard,
		CommonsImage
	},
	props: {
		list: {
			type: Object,
			default: null,
			required: true
		}
	},
	data: () => ( {
		listInfo: false
	} ),
	methods: {
		closeListInfo() {
			this.listInfo = false;
		}
	}
};
</script>
