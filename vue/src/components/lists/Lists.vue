<template>
	<v-container>
		<v-row>
			<v-col v-for="list in lists.results"
				:key="list.id"
				class="lists px-0 pb-0"
				cols="12"
			>
				<ListCard :list="list"
					:list-footer="listFooter"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import ListCard from '@/components/lists/ListCard';

export default {
	name: 'Lists',
	components: {
		ListCard
	},
	props: {
		lists: {
			type: Object,
			default: null
		},
		listFooter: {
			type: Boolean
		}
	}
};
</script>
