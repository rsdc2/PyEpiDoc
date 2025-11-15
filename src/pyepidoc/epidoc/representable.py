from __future__ import annotations

from typing import (
    Optional, 
    Sequence, 
    Union
)
from functools import cached_property, reduce

from lxml.etree import (
    _Element, 
    _Comment, 
    _ElementUnicodeResult
)

from pyepidoc.xml.utils import localname

from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.shared.enums import RegTextType
from .edition_element import EditionElement

Node = Union[_Element, _ElementUnicodeResult]


class Representable(EditionElement):

    @property
    def elem_classes(self) -> dict[str, type[Representable]]:
        from .representable_classes import representable_classes
        return representable_classes

    @property
    def form_normalized(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>, <surplus> and <del> elements
        """
        return self.normalized_form
    
    @property
    def leiden_form(self) -> str:
        """
        Returns the form per Leiden conventions, i.e. with
        abbreviations expanded with brackets
        """
        if self.representable_cls_inst is None:
            return self.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_form`.')
        return self.representable_cls_inst.leiden_form

    @property
    def leiden_plus_form(self) -> str:
        """
        Returns the Leiden form, with 
        interpunts indicated by middle dot;
        line breaks are indicated with vertical bar '|'
        """

        def string_rep(n: Node) -> str:
            ln = localname(n)

            if ln in ['g', 'lb', 'gap']:
                return self.elem_classes[ln](n).leiden_form
            
            return ''

        def get_next_non_text(
                acc: list[Node],
                node: Node
            ) -> list[Node]:

            if acc != []:
                last = acc[-1]

                if type(last) is _ElementUnicodeResult:
                    if str(last).strip() not in ['', '·']:
                        return acc 
                
                if localname(last) in ['lb', 'w', 'name', 'persName', 'roleName', 'num']:
                    return acc
            
            return acc + [node]

        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_plus_form`.')
        
        preceding = reversed([e for e in self.preceding_nodes_in_ab])
        following = [e for e in self.following_nodes_in_ab]

        preceding_upto_text: list[Node] = \
            list(reversed(reduce(
                get_next_non_text, # type: ignore 
                preceding, 
                list[Node]()))) # type: ignore
        following_upto_text: list[Node] = reduce(get_next_non_text, following, [])
        
        prec_text = ''.join(map(string_rep, preceding_upto_text))
        following_text = ''.join(map(string_rep, following_upto_text))

        return prec_text + self.leiden_form + following_text        

    @cached_property
    def simple_lemmatized_edition_element(self) -> EditionElement:
        """
        Element for use in simple-lemmatized edition
        """
        t = type(self)
        elem = t(self.deepcopy().e)
        elem.remove_children()
        elem.remove_attr('id', XMLNS)
        elem.text = self.simple_lemmatized_edition_form
        return elem
    
    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        """
        Form for use as text in the simple_lemmatized_edition_element
        """
        return self.normalized_form

    @cached_property
    def normalized_form(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @orig_form
        """
        
        if self.representable_cls_inst is None:
            return self.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `normalized_form`.')
        return self.representable_cls_inst.normalized_form
    
    @cached_property
    def orig_form(self) -> str:
        """
        Returns the original form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @normalized_form
        """
        non_ancestors = RegTextType.values()

        ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                 for ancestor in non_ancestors])

        normalized_text = self.xpath(f'descendant::text()[{ancestors_str}]')
        return self._clean_text(''.join([str(t) for t in normalized_text]))
    
    @property
    def representable_cls_inst(self) -> Representable | None:
        """
        An instance of a class inheriting from Representable giving 
        behaviours specific to the element in question, e.g. W, G, Expan etc.
        """

        cls = self.elem_classes.get(self.localname)
        if cls is None:
            return None
        inst = cls(self._e)
        return inst

    @property
    def type(self) -> str:
        return self.tag.name
