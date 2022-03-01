<template>
	<v-container>
		<v-row v-if="!lists.results">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'lists-nolistsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col v-for="list in lists.results"
				:key="list.id"
				class="lists"
				cols="12"
			>
				<ListCard :list="list" :list-footer="listFooter" />
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
