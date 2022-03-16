<template>
	<div v-frag>
		<v-text-field
			v-if="widget === 'text'"
			v-model="model"
			:required="ui.required"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:counter="schema.maxLength"
			clearable
			@update:error="emitIsValid"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-text-field>
		<v-textarea
			v-else-if="widget === 'multiline'"
			v-model="model"
			:required="ui.required"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:counter="schema.maxLength"
			rows="1"
			auto-grow
			clearable
			@update:error="emitIsValid"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-textarea>
		<v-autocomplete
			v-else-if="widget === 'select'"
			v-model="model"
			:label="ui.label"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			:items="ui.select.items()"
			:multiple="ui.multiple || false"
			:deletable-chips="ui.multiple || false"
			:small-chips="ui.multiple || false"
			:clearable="ui.multiple ? false : true"
			@update:error="emitIsValid"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-autocomplete>
		<v-combobox
			v-else-if="widget === 'multi-select'"
			v-model="model"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			multiple
			deletable-chips
			small-chips
			@update:error="emitIsValid"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-combobox>
		<v-combobox
			v-else-if="widget === 'multi-select-tool'"
			v-model="model"
			:loading="toolAutoCompleteLoading"
			:search-input.sync="toolAutoComplete"
			:menu-props="menuProps"
			:items="getToolAutoCompleteResultsArr()"
			:rules="validationRules"
			:prepend-icon="ui.icon"
			:hint="schema.description"
			hide-selected
			multiple
			deletable-chips
			small-chips
			@update:error="emitIsValid"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
			<template #item="data">
				<v-list-item-content>
					<v-list-item-title>
						<dl class="row ma-0">
							<dt class="me-1">{{ toolAutoCompleteResults[data.item][0] }}</dt>
							<dd>({{ toolAutoCompleteResults[data.item][1] }})</dd>
						</dl>
					</v-list-item-title>
				</v-list-item-content>
			</template>

			<template v-if="!toolAutoCompleteLoading" #no-data>
				<v-list-item>
					<v-list-item-content>
						<v-list-item-title>
							{{ $t( 'tool-not-found', [ toolAutoComplete ] ) }}
						</v-list-item-title>
					</v-list-item-content>
				</v-list-item>
			</template>
		</v-combobox>
		<template v-else-if="widget === 'authors' || widget === 'url-multilingual'">
			<v-combobox
				v-model="model"
				:hint="schema.description"
				:prepend-icon="ui.icon"
				:append-icon="ui.appendIcon"
				multiple
				readonly
				@click:append="showItemDialog( null, null )"
				@click="showItemDialog( null, null )"
				@update:error="emitIsValid"
			>
				<template #label>
					<InputLabel :label="ui.label" :required="ui.required" />
				</template>
				<template #selection="{ item, index, parent }">
					<v-chip
						class="ma-2"
						close
						@click:close="parent.selectItem( item )"
						@click="showItemDialog( item, index )"
					>
						<span v-if="widget === 'authors'">
							{{ item.name }}
						</span>
						<span v-else-if="widget === 'url-multilingual'">
							{{ `${getLocaleText( item.language )}: ` }}{{ item.url }}
						</span>
					</v-chip>
				</template>
			</v-combobox>
			<ItemDialog
				:ui-schema="ui.items"
				:schema="schema.items"
				:items.sync="model"
				:item-edit.sync="itemEdit"
			/>
		</template>
		<v-checkbox
			v-else-if="widget === 'checkbox'"
			v-model="model"
			@update:error="emitIsValid"
		>
			<template #label>
				<InputLabel :label="ui.label" :required="ui.required" />
			</template>
		</v-checkbox>
		<pre v-else>
			{{ schema }}
		</pre>
	</div>
</template>

<script>
import { mapState } from 'vuex';
import patternRegexRule from '@/plugins/pattern-regex';
import InputLabel from '@/components/common/InputLabel';
import { isValidHttpUrl } from '@/helpers/validation';

export const methods = {
	/**
	 * Initialize our model based on our value and schema.
	 */
	initModel() {
		if ( this.value ) {
			if (
				this.schema.type === 'object' &&
				Object.keys( this.value ).length > 0
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'array' &&
				this.value.length > 0
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'boolean' &&
				this.value !== null
			) {
				this.model = this.value;
			} else if (
				this.schema.type === 'string' ||
				this.schema.type === 'number' ||
				this.schema.type === 'integer'
			) {
				this.model = this.value;
			} else {
				this.model = this.initBlankValue();
			}
		} else {
			this.model = this.initBlankValue();
		}
	},

	initBlankValue() {
		switch ( this.schema.type ) {
			case 'object':
				return {};
			case 'array':
				return [];
			case 'boolean':
				return false;
			case 'number':
			case 'integer':
			default:
				return null;
		}
	},
	performToolAutoComplete( v ) {
		this.toolAutoCompleteLoading = true;
		this.$store.dispatch( 'search/autoCompleteTools', v ).finally(
			() => {
				this.toolAutoCompleteLoading = false;
			}
		);
	},
	getToolAutoCompleteResultsArr() {
		return this.toolAutoCompleteResults ?
			Object.keys( this.toolAutoCompleteResults ) :
			[];
	},
	/**
	 * Populate and open the showItemDialog.
	 *
	 * @param {?Object} item - item representing an entry in array field.
	 * @param {?number} index - Author position in the authors array.
	 */
	showItemDialog( item, index ) {
		this.itemEdit.item = item;
		this.itemEdit.index = index;

		if ( !item && this.widget === 'url-multilingual' ) {
			this.itemEdit.item = { language: this.$i18n.locale, url: null };
		}

		this.itemEdit.itemDialogOpen = true;
	},
	getLocaleText( code ) {
		this.localeSelect.some(
			( locale ) => {
				if ( locale.value === code ) {
					code = locale.text;
					return true;
				}
				return false;
			}
		);
		return code;
	},
	emitIsValid( val ) {
		this.$emit( 'is-valid', val );
	}
};

export default {
	name: 'InputWidget',
	components: {
		InputLabel,
		// Import via function to work around circular dependency between
		// ItemDialog and InputWidget components.
		ItemDialog: () => import( '@/components/common/ItemDialog' )
	},
	props: {
		schema: {
			type: Object,
			default: () => {},
			required: true
		},
		uiSchema: {
			type: Object,
			default: () => {}
		},
		value: {
			type: [ String, Number, Boolean, Array, Object ],
			default: null
		}
	},
	data: () => ( {
		model: null,
		toolAutoCompleteLoading: false,
		itemEdit: {
			index: null,
			item: null,
			itemDialogOpen: false
		},
		toolAutoComplete: null
	} ),
	computed: {
		/**
		 * Get our UI helper data.
		 *
		 * @return {Object}
		 */
		ui() {
			return this.schema[ 'x-ui' ] || this.uiSchema;
		},
		widget() {
			if ( this.ui.widget ) {
				return this.ui.widget;
			}
			if ( this.schema.type === 'string' ) {
				if ( this.schema.enum ) {
					return 'select';
				}
				return this.schema.maxLength > 2047 ? 'multiline' : 'text';
			}
			return this.schema.type;
		},
		menuProps() {
			return !this.toolAutoComplete ? { value: false } : {};
		},
		validationRules() {
			const schema = this.schema;
			const ui = this.ui;
			const rules = [];
			if ( schema.maxLength ) {
				rules.push(
					( v ) => ( v || '' ).length <= schema.maxLength ||
						this.$t( 'charslimit', [ schema.maxLength ] )
				);
			}
			if ( schema.pattern ) {
				rules.push( ...patternRegexRule( schema.pattern ) );
			}
			if ( schema.format === 'uri' ) {
				rules.push(
					( v ) => !v ? true : isValidHttpUrl( v ) ||
					this.$t( 'urlinvalid' )
				);
			}
			if ( ui.required === true ) {
				rules.push( ( v ) => !!v || this.$t( 'required-field' ) );
			}
			return rules;
		},
		...mapState( 'search', {
			toolAutoCompleteResults: 'toolAutoCompleteResults'
		} ),
		...mapState( 'locale', [ 'localeSelect' ] )
	},
	methods,
	watch: {
		toolAutoComplete: {
			handler( val ) {
				if ( val && val !== this.model ) {
					this.performToolAutoComplete( val );
				}
			}
		},
		model: {
			handler( newVal ) {
				this.$emit( 'input', newVal );
			},
			deep: true,
			immediate: true
		},
		value: {
			handler( newVal, oldVal ) {
				if ( JSON.stringify( oldVal ) !== JSON.stringify( newVal ) ) {
					this.initModel();
				}
			},
			deep: true
		}
	},
	created() {
		this.initModel();
	}
};
</script>
