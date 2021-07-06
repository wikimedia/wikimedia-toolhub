<template>
	<v-container v-if="list">
		<v-card
			elevation="0"
			class="list-card__card"
		>
			<v-card-title>
				<CommonsImage
					:commons-url="list.icon"
					:size="50"
					class="me-2"
				/>
				<h2 class="list-card__title text-h4 me-2">
					{{ list.title }}
				</h2>
				<v-chip
					v-if="list.featured"
					color="utility_yellow30"
					text-color="bgtext"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon size="15" class="me-1">
						mdi-star
					</v-icon>
					{{ $t( 'listinfo-featuredlist' ) }}
				</v-chip>
			</v-card-title>

			<v-card-text>
				<v-row>
					<v-col cols="12">
						<div
							class="text--primary text-subtitle-1"
							dir="auto"
						>
							{{ list.description }}
						</div>
					</v-col>
				</v-row>

				<v-row>
					<v-col
						lg="2"
						md="6"
						cols="12"
					>
						<dl class="list-card__authors row pt-1 text-subtitle-1">
							<dt class="me-1">{{ $t( 'authors' ) }}:</dt>
							<dd class="line-clamp">{{ list.created_by.username }}</dd>
						</dl>
					</v-col>

					<v-col md="6" cols="12">
						<dl class="row pt-1 text-subtitle-1">
							<dt class="me-1">{{ $t( 'datecreated' ) }}:</dt>
							<dd>{{ list.created_date | moment( 'lll' ) }}</dd>
						</dl>
					</v-col>

					<v-col
						lg="4"
						md="12"
						cols="12"
						class="py-1 px-0 text-md-end"
					>
						<v-btn
							text
							transparent
							color="primary"
							:small="$vuetify.breakpoint.smAndDown"
							@click="copyToClipboard"
						>
							<v-icon class="me-2">
								mdi-link-variant
							</v-icon>
							{{ $t( 'listinfo-copylink' ) }}
						</v-btn>
					</v-col>
				</v-row>

				<v-row v-if="showClipboardMsg">
					<v-col class="py-1 px-0 text-md-end">
						{{ $t( 'copiedtoclipboard' ) }}
					</v-col>
				</v-row>
			</v-card-text>
		</v-card>

		<v-divider />

		<v-row class="my-2">
			<v-col v-for="tool in list.tools"
				:key="tool.name"
				class="lists pa-0"
			>
				<v-card
					class="ma-4"
					min-width="210"
				>
					<ToolCard :tool="tool" />
				</v-card>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState, mapMutations } from 'vuex';
import CommonsImage from '@/components/common/CommonsImage';
import ToolCard from '@/components/tools/ToolCard';

export default {
	name: 'ListInfo',
	components: {
		CommonsImage,
		ToolCard
	},
	data() {
		return {
			showClipboardMsg: false,
			id: this.$route.params.id
		};
	},
	computed: {
		...mapState( 'lists', [ 'list' ] )
	},
	methods: {
		...mapMutations( 'lists', [ 'LIST' ] ),
		getListInfo() {
			this.$store.dispatch( 'lists/getListInfo', this.id );
		},
		copyToClipboard() {
			const fullUrl = window.location.origin + this.$route.path;
			this.$copyText( fullUrl ).then( () => {
				this.showClipboardMsg = true;
				setTimeout( () => {
					this.showClipboardMsg = false;
				}, 20000 );
			}, this );
		}
	},
	mounted() {
		// Clear any data from a prior view
		this.LIST( null );
		this.getListInfo();
	}
};
</script>
