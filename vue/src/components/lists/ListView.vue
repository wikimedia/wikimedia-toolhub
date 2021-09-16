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

			<v-col cols="auto" class="list-action">
				<v-btn
					class="my-3"
					icon
					:to="{ name: 'list', params: { id: list.id } }"
				>
					<v-icon size="30" color="base20">
						mdi-link-variant
					</v-icon>
				</v-btn>
			</v-col>

			<v-col v-if="list.description"
				cols="auto"
				class="list-action"
			>
				<v-btn
					class="my-3"
					icon
					@click="listInfo = !listInfo"
				>
					<v-icon size="30" color="base20">
						mdi-information-outline
					</v-icon>
				</v-btn>
			</v-col>
		</v-row>
		<v-alert
			class="ma-2"
			:value="listInfo"
			color="accent"
			dismissible
			@input="closeListInfo"
		>
			{{ list.description }}
		</v-alert>
		<v-sheet>
			<v-card
				v-if="list.tools.length === 0"
				class="ma-4"
				elevation="0"
			>
				<v-card-title class="pa-0">{{ $t( 'lists-listempty' ) }}</v-card-title>
			</v-card>
			<v-slide-group
				v-else
				show-arrows="always"
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
import CommonsImage from '@/components/common/CommonsImage';

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
