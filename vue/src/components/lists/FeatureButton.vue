<template>
	<v-btn
		v-if="userAuthed && list.featured"
		:small="$vuetify.breakpoint.smAndDown"
		class="ms-4"
		color="yellow50"
		@click="unfeatureList"
	>
		<v-icon class="me-2">
			mdi-star
		</v-icon>
		{{ $t( 'featured' ) }}
	</v-btn>
	<v-btn
		v-else-if="userAuthed"
		:small="$vuetify.breakpoint.smAndDown"
		class="ms-4"
		@click="featureList"
	>
		<v-icon class="me-2">
			mdi-star-outline
		</v-icon>
		{{ $t( 'feature' ) }}
	</v-btn>
</template>

<script>
export default {
	name: 'FeatureButton',
	props: {
		list: {
			type: Object,
			default: null
		}
	},
	data() {
		return {
			page: 1,
			userAuthed: this.$can( 'feature', 'lists/toollist' )
		};
	},
	methods: {
		featureList() {
			this.$store.dispatch( 'lists/featureList', this.list.id );
		},
		unfeatureList() {
			this.$store.dispatch( 'lists/unfeatureList', this.list.id );
		}
	}
};
</script>
